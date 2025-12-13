from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Q
from .validators import (
    validate_booking_advance,
    validate_weekday,
    validate_business_hours,
    validate_minimum_duration,
    validate_maximum_duration,
    validate_user_booking_limit,
)


class Agendamento(models.Model):
	STATUS_CHOICES = [
		('P', 'Pendente'),
		('A', 'Aprovado'),
		('R', 'Reprovado'),
	]

	usuario = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name='agendamentos'
	)
	sala = models.ForeignKey(
		'salas.Sala',
		on_delete=models.PROTECT,
		related_name='agendamentos'
	)
	data = models.DateField()
	horario_inicio = models.TimeField()
	horario_fim = models.TimeField()
	motivo = models.TextField(blank=True)
	status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
	justificativa_reprovacao = models.TextField(blank=True, null=True)
	criado_em = models.DateTimeField(auto_now_add=True)
	atualizado_em = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-data', 'horario_inicio']
		verbose_name = 'Agendamento'
		verbose_name_plural = 'Agendamentos'
		indexes = [
			models.Index(fields=['data', 'status']),
			models.Index(fields=['usuario', 'status']),
			models.Index(fields=['sala', 'data', 'status']),
		]

	def __str__(self):
		return f"#{self.pk} - {self.sala} em {self.data} ({self.horario_inicio}–{self.horario_fim})"

	def clean(self):
		"""Validações completas do agendamento"""
		super().clean()

		# Validação 1: Horário de início deve ser anterior ao fim
		if self.horario_inicio and self.horario_fim:
			if self.horario_inicio >= self.horario_fim:
				raise ValidationError({
					'horario_inicio': 'Horário de início deve ser anterior ao horário de fim.'
				})
			
			# Validação 2: Duração mínima e máxima
			validate_minimum_duration(self.horario_inicio, self.horario_fim)
			validate_maximum_duration(self.horario_inicio, self.horario_fim)
			
			# Validação 3: Horário comercial
			validate_business_hours(self.horario_inicio, self.horario_fim)

		# Validação 4: Data válida (antecedência e dia da semana)
		if self.data:
			validate_booking_advance(self.data)
			validate_weekday(self.data)

		# Validação 5: Limite de agendamentos por usuário
		if self.usuario and self.data:
			validate_user_booking_limit(self.usuario, self.data)

		# Validação 6: Conflitos com agendamentos APROVADOS existentes
		if self.sala and self.data and self.horario_inicio and self.horario_fim:
			conflicts = Agendamento.objects.filter(
				sala=self.sala,
				data=self.data,
				status='A'  # apenas agendamentos aprovados bloqueiam
			).exclude(pk=self.pk).filter(
				~(
					Q(horario_fim__lte=self.horario_inicio) |
					Q(horario_inicio__gte=self.horario_fim)
				)
			)

			if conflicts.exists():
				conflict = conflicts.first()
				raise ValidationError(
					f'Conflito de horário: sala já reservada de '
					f'{conflict.horario_inicio.strftime("%H:%M")} às '
					f'{conflict.horario_fim.strftime("%H:%M")}.'
				)

	def save(self, *args, **kwargs):
		"""Garante validação antes de salvar"""
		self.full_clean()
		return super().save(*args, **kwargs)
	
	def pode_cancelar(self):
		"""Verifica se o agendamento pode ser cancelado"""
		from .validators import validate_cancellation_time
		try:
			validate_cancellation_time(self)
			return True
		except ValidationError:
			return False
	
	def cancelar(self, motivo=''):
		"""Cancela o agendamento"""
		from .validators import validate_cancellation_time
		validate_cancellation_time(self)
		
		self.status = 'R'
		self.justificativa_reprovacao = f'Cancelado pelo usuário. {motivo}'
		self.save()
		
		# Enviar notificação
		from .tasks import send_booking_notification_async
		send_booking_notification_async.delay(self.id, 'cancelled')

