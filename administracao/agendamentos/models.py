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
		"""Validações básicas do agendamento"""
		# Validação simples: horário de início antes do fim
		if self.horario_inicio and self.horario_fim:
			if self.horario_inicio >= self.horario_fim:
				raise ValidationError('Horário de início deve ser anterior ao horário de fim.')

	def save(self, *args, **kwargs):
		"""Salva o agendamento"""
		# Validação já é feita pelo formulário
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

