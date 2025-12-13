from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from administracao.models import Perfil


@receiver(post_save, sender=User)
def criar_perfil_usuario(sender, instance, created, **kwargs):
    """
    Signal que cria automaticamente um Perfil quando um novo usuário é criado.
    Padrão: tipo='PRO' (Professor).
    """
    if created:
        Perfil.objects.get_or_create(
            usuario=instance,
            defaults={'tipo': 'PRO'}
        )


@receiver(post_save, sender=User)
def salvar_perfil_usuario(sender, instance, **kwargs):
    """
    Garante que o Perfil seja salvo sempre que o User for salvo.
    """
    if hasattr(instance, 'perfil'):
        instance.perfil.save()
