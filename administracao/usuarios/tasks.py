"""
Celery tasks for usuarios app.
"""
from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_welcome_email_with_password(self, user_id, senha_temporaria):
    """
    Envia email de boas-vindas com senha temporária para novo usuário.
    
    Args:
        user_id: ID do usuário
        senha_temporaria: Senha temporária gerada
    """
    try:
        from django.contrib.auth.models import User
        
        user = User.objects.get(pk=user_id)
        
        # Renderizar email HTML
        html_message = render_to_string('emails/usuario_criado.html', {
            'usuario': user,
            'senha_temporaria': senha_temporaria,
            'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000',
        })
        
        # Enviar email
        send_mail(
            subject='🎉 Bem-vindo ao AgendeAqui!',
            message=f"""
Olá {user.get_full_name() or user.username},

Sua conta foi criada com sucesso no sistema AgendeAqui!

Seus dados de acesso:
- Usuário: {user.username}
- Email: {user.email}
- Senha temporária: {senha_temporaria}

Por favor, faça login e altere sua senha no primeiro acesso.

Atenciosamente,
Equipe AgendeAqui
            """.strip(),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f'Email de boas-vindas enviado para {user.email}')
        
    except User.DoesNotExist:
        logger.error(f'Usuário #{user_id} não encontrado')
    except Exception as exc:
        logger.error(f'Erro ao enviar email para usuário #{user_id}: {exc}')
        # Retry task
        raise self.retry(exc=exc, countdown=60 * 5)  # Retry after 5 minutes


@shared_task(bind=True, max_retries=3)
def send_password_reset_email(self, user_id, nova_senha):
    """
    Envia email com nova senha após redefinição pelo admin.
    
    Args:
        user_id: ID do usuário
        nova_senha: Nova senha gerada
    """
    try:
        from django.contrib.auth.models import User
        
        user = User.objects.get(pk=user_id)
        
        # Renderizar email HTML
        html_message = render_to_string('emails/senha_redefinida.html', {
            'usuario': user,
            'nova_senha': nova_senha,
            'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000',
        })
        
        # Enviar email
        send_mail(
            subject='🔑 Senha Redefinida - AgendeAqui',
            message=f"""
Olá {user.get_full_name() or user.username},

Sua senha foi redefinida por um administrador.

Nova senha temporária: {nova_senha}

Por favor, faça login e altere sua senha.

Atenciosamente,
Equipe AgendeAqui
            """.strip(),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f'Email de redefinição de senha enviado para {user.email}')
        
    except User.DoesNotExist:
        logger.error(f'Usuário #{user_id} não encontrado')
    except Exception as exc:
        logger.error(f'Erro ao enviar email para usuário #{user_id}: {exc}')
        raise self.retry(exc=exc, countdown=60 * 5)
