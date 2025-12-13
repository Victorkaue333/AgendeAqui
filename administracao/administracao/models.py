# Celery app initialization
from .celery import app as celery_app

__all__ = ('celery_app',)

from django.db import models
from django.conf import settings


class Perfil(models.Model):
    PERFIL_CHOICES = [
        ('ADM', 'Administrador'),
        ('COO', 'Coordenador'),
        ('PRO', 'Professor'),
    ]

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfil'
    )
    tipo = models.CharField(max_length=3, choices=PERFIL_CHOICES, default='PRO')
    telefone = models.CharField(max_length=20, blank=True)
    departamento = models.CharField(max_length=100, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.get_full_name() or self.usuario.username} ({self.get_tipo_display()})"


class Configuracao(models.Model):
    chave = models.CharField(max_length=100, unique=True)
    valor = models.TextField(blank=True)
    descricao = models.TextField(blank=True)

    def __str__(self):
        return self.chave

    class Meta:
        verbose_name = 'Configuração'
        verbose_name_plural = 'Configurações'


class AuditLog(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    acao = models.CharField(max_length=200)
    objeto = models.CharField(max_length=200, blank=True)
    dados = models.JSONField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Log de Auditoria'
        verbose_name_plural = 'Logs de Auditoria'

    def __str__(self):
        usuario = self.usuario.username if self.usuario else 'Sistema'
        return f"{self.criado_em.isoformat()} - {usuario} - {self.acao}"
 