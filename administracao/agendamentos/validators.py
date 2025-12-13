"""
Validators customizados para o sistema AgendeAqui.
"""
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
from datetime import datetime, timedelta, time


def validate_booking_advance(data):
    """
    Valida se o agendamento está dentro do prazo permitido.
    """
    hoje = timezone.now().date()
    
    # Antecedência mínima
    min_advance = timedelta(hours=getattr(settings, 'MIN_BOOKING_ADVANCE_HOURS', 2))
    earliest = timezone.now() + min_advance
    
    if data < earliest.date():
        raise ValidationError(
            f'Agendamentos devem ser feitos com pelo menos {settings.MIN_BOOKING_ADVANCE_HOURS} horas de antecedência.'
        )
    
    # Antecedência máxima
    max_advance = timedelta(days=getattr(settings, 'MAX_BOOKING_ADVANCE_DAYS', 30))
    latest = hoje + max_advance
    
    if data > latest:
        raise ValidationError(
            f'Agendamentos só podem ser feitos com até {settings.MAX_BOOKING_ADVANCE_DAYS} dias de antecedência.'
        )


def validate_weekday(data):
    """
    Valida se a data é em um dia da semana permitido.
    """
    allowed_weekdays = getattr(settings, 'ALLOWED_WEEKDAYS', [0, 1, 2, 3, 4, 5])
    
    if data.weekday() not in allowed_weekdays:
        dias_semana = {
            0: 'Segunda-feira',
            1: 'Terça-feira',
            2: 'Quarta-feira',
            3: 'Quinta-feira',
            4: 'Sexta-feira',
            5: 'Sábado',
            6: 'Domingo'
        }
        dia_nome = dias_semana.get(data.weekday(), 'Este dia')
        raise ValidationError(
            f'{dia_nome} não está disponível para agendamentos.'
        )


def validate_business_hours(horario_inicio, horario_fim):
    """
    Valida se o horário está dentro do expediente da instituição.
    """
    # Parse das configurações
    open_time_str = getattr(settings, 'INSTITUTION_OPEN_TIME', '07:00')
    close_time_str = getattr(settings, 'INSTITUTION_CLOSE_TIME', '22:00')
    
    open_time = datetime.strptime(open_time_str, '%H:%M').time()
    close_time = datetime.strptime(close_time_str, '%H:%M').time()
    
    if horario_inicio < open_time:
        raise ValidationError({
            'horario_inicio': f'A instituição abre às {open_time_str}. Escolha um horário posterior.'
        })
    
    if horario_fim > close_time:
        raise ValidationError({
            'horario_fim': f'A instituição fecha às {close_time_str}. Escolha um horário anterior.'
        })


def validate_minimum_duration(horario_inicio, horario_fim):
    """
    Valida duração mínima do agendamento (30 minutos).
    """
    duracao = datetime.combine(datetime.today(), horario_fim) - datetime.combine(datetime.today(), horario_inicio)
    
    if duracao < timedelta(minutes=30):
        raise ValidationError(
            'O agendamento deve ter duração mínima de 30 minutos.'
        )


def validate_maximum_duration(horario_inicio, horario_fim):
    """
    Valida duração máxima do agendamento (8 horas).
    """
    duracao = datetime.combine(datetime.today(), horario_fim) - datetime.combine(datetime.today(), horario_inicio)
    
    if duracao > timedelta(hours=8):
        raise ValidationError(
            'O agendamento não pode ter duração superior a 8 horas.'
        )


def validate_user_booking_limit(usuario, data):
    """
    Valida se o usuário não excedeu o limite de agendamentos por semana.
    """
    from agendamentos.models import Agendamento
    
    # Calcular início e fim da semana
    inicio_semana = data - timedelta(days=data.weekday())
    fim_semana = inicio_semana + timedelta(days=6)
    
    # Contar agendamentos do usuário na semana
    count = Agendamento.objects.filter(
        usuario=usuario,
        data__gte=inicio_semana,
        data__lte=fim_semana,
        status='A'  # Apenas aprovados
    ).count()
    
    max_bookings = getattr(settings, 'MAX_BOOKINGS_PER_USER_PER_WEEK', 5)
    
    if count >= max_bookings:
        raise ValidationError(
            f'Você atingiu o limite de {max_bookings} agendamentos por semana.'
        )


def validate_cancellation_time(agendamento):
    """
    Valida se o cancelamento está sendo feito com antecedência mínima.
    """
    min_cancellation_hours = getattr(settings, 'MIN_CANCELLATION_HOURS', 24)
    min_cancellation = timedelta(hours=min_cancellation_hours)
    
    agendamento_datetime = datetime.combine(agendamento.data, agendamento.horario_inicio)
    now = timezone.now()
    
    if timezone.make_aware(agendamento_datetime) - now < min_cancellation:
        raise ValidationError(
            f'Cancelamentos devem ser feitos com pelo menos {min_cancellation_hours} horas de antecedência.'
        )
