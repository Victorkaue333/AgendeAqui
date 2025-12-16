from django.conf import settings
from django.db import models


class Notificacao(models.Model):
    NIVEL_CHOICES = [
        ('info', 'Informação'),
        ('success', 'Sucesso'),
        ('warning', 'Aviso'),
        ('danger', 'Erro'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notificacoes',
    )
    titulo = models.CharField(max_length=120)
    mensagem = models.TextField()
    nivel = models.CharField(max_length=10, choices=NIVEL_CHOICES, default='info')
    url = models.CharField(max_length=300, blank=True, default='')

    lida = models.BooleanField(default=False)
    criada_em = models.DateTimeField(auto_now_add=True)
    lida_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-criada_em']
        verbose_name = 'Notificação'
        verbose_name_plural = 'Notificações'
        indexes = [
            models.Index(fields=['usuario', 'lida', '-criada_em']),
        ]

    def __str__(self) -> str:
        return f"{self.usuario_id} - {self.titulo}"
