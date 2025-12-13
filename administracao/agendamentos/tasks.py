"""
Celery tasks for agendamentos app.
"""
from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta
from .models import Agendamento
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_booking_notification_async(self, agendamento_id, notification_type):
    """
    Enviar notificação de agendamento de forma assíncrona.
    
    Args:
        agendamento_id: ID do agendamento
        notification_type: 'approved', 'rejected', 'cancelled', 'reminder'
    """
    try:
        agendamento = Agendamento.objects.select_related('usuario', 'sala').get(pk=agendamento_id)
        usuario = agendamento.usuario
        
        # Templates de email
        templates = {
            'approved': {
                'subject': '✅ Agendamento Aprovado - AgendeAqui',
                'template': 'emails/agendamento_aprovado.html'
            },
            'rejected': {
                'subject': '❌ Agendamento Reprovado - AgendeAqui',
                'template': 'emails/agendamento_reprovado.html'
            },
            'cancelled': {
                'subject': '🚫 Agendamento Cancelado - AgendeAqui',
                'template': 'emails/agendamento_cancelado.html'
            },
            'reminder': {
                'subject': '⏰ Lembrete: Agendamento Amanhã - AgendeAqui',
                'template': 'emails/agendamento_lembrete.html'
            },
        }
        
        if notification_type not in templates:
            raise ValueError(f'Invalid notification type: {notification_type}')
        
        template_config = templates[notification_type]
        
        # Renderizar email
        html_message = render_to_string(template_config['template'], {
            'agendamento': agendamento,
            'usuario': usuario,
        })
        
        # Enviar email
        send_mail(
            subject=template_config['subject'],
            message='',  # Plain text fallback
            from_email=None,  # Use DEFAULT_FROM_EMAIL
            recipient_list=[usuario.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f'Email {notification_type} sent to {usuario.email} for booking #{agendamento_id}')
        
    except Agendamento.DoesNotExist:
        logger.error(f'Agendamento #{agendamento_id} not found')
    except Exception as exc:
        logger.error(f'Error sending email for booking #{agendamento_id}: {exc}')
        # Retry task
        raise self.retry(exc=exc, countdown=60 * 5)  # Retry after 5 minutes


@shared_task
def send_booking_reminders():
    """
    Enviar lembretes para agendamentos que acontecerão nas próximas 24 horas.
    Executado diariamente pelo Celery Beat.
    """
    tomorrow = timezone.now() + timedelta(days=1)
    tomorrow_start = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow_end = tomorrow.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    # Buscar agendamentos aprovados para amanhã
    agendamentos = Agendamento.objects.filter(
        status='A',
        data__gte=tomorrow_start.date(),
        data__lte=tomorrow_end.date()
    ).select_related('usuario', 'sala')
    
    count = 0
    for agendamento in agendamentos:
        send_booking_notification_async.delay(agendamento.id, 'reminder')
        count += 1
    
    logger.info(f'Sent {count} booking reminders')
    return f'Sent {count} reminders'


@shared_task
def cleanup_expired_bookings():
    """
    Limpar agendamentos pendentes expirados (mais de 30 dias).
    Executado diariamente pelo Celery Beat.
    """
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    deleted_count, _ = Agendamento.objects.filter(
        status='P',
        criado_em__lt=thirty_days_ago
    ).delete()
    
    logger.info(f'Deleted {deleted_count} expired pending bookings')
    return f'Deleted {deleted_count} bookings'


@shared_task(bind=True, max_retries=3)
def export_report_async(self, user_id, filters):
    """
    Gerar relatório de forma assíncrona e enviar por email.
    """
    # TODO: Implementar exportação de relatórios
    pass
