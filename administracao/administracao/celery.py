"""
Celery configuration for AgendeAqui project.
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'administracao.settings')

app = Celery('agendeaqui')

# Load configuration from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()

# Periodic Tasks Configuration
app.conf.beat_schedule = {
    # Enviar lembretes de agendamentos (24h antes)
    'send-booking-reminders': {
        'task': 'agendamentos.tasks.send_booking_reminders',
        'schedule': crontab(hour=9, minute=0),  # Diariamente às 9h
    },
    # Limpar agendamentos expirados
    'cleanup-expired-bookings': {
        'task': 'agendamentos.tasks.cleanup_expired_bookings',
        'schedule': crontab(hour=1, minute=0),  # Diariamente à 1h
    },
}

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Task de debug para testar Celery"""
    print(f'Request: {self.request!r}')
