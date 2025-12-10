#!/usr/bin/env python
import os
import django

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'administracao.settings')
django.setup()

from django.contrib.auth.models import User
from agendamentos.models import Agendamento
from salas.models import Sala, Bloco
from datetime import datetime, timedelta

# Pega o admin user
admin_user = User.objects.get(username='admin')

# Cria bloco se não existir
bloco, _ = Bloco.objects.get_or_create(nome="Bloco Principal")

# Cria salas de teste se não existirem
sala1, _ = Sala.objects.get_or_create(nome="Sala 1", defaults={"capacidade": 30, "bloco": bloco})
sala2, _ = Sala.objects.get_or_create(nome="Lab Python", defaults={"capacidade": 20, "bloco": bloco})
sala3, _ = Sala.objects.get_or_create(nome="Auditório", defaults={"capacidade": 100, "bloco": bloco})

# Cria agendamentos de teste
hoje = datetime.now().date()
hora_inicio = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0).time()
hora_fim = datetime.now().replace(hour=12, minute=0, second=0, microsecond=0).time()

# Agendamento 1 - Aprovado (futuro)
Agendamento.objects.create(
    usuario=admin_user,
    sala=sala1,
    data=hoje + timedelta(days=2),
    horario_inicio=hora_inicio,
    horario_fim=hora_fim,
    motivo="Reunião de planejamento",
    status="A"
)

# Agendamento 2 - Pendente
Agendamento.objects.create(
    usuario=admin_user,
    sala=sala2,
    data=hoje + timedelta(days=5),
    horario_inicio=hora_inicio,
    horario_fim=hora_fim,
    motivo="Aula de programação",
    status="P"
)

# Agendamento 3 - Aprovado
Agendamento.objects.create(
    usuario=admin_user,
    sala=sala3,
    data=hoje + timedelta(days=1),
    horario_inicio=hora_inicio,
    horario_fim=hora_fim,
    motivo="Palestra acadêmica",
    status="A"
)

# Agendamento 4 - Reprovado
Agendamento.objects.create(
    usuario=admin_user,
    sala=sala1,
    data=hoje - timedelta(days=3),
    horario_inicio=hora_inicio,
    horario_fim=hora_fim,
    motivo="Workshop cancelado",
    status="R"
)

print(f"✓ {Agendamento.objects.count()} agendamentos criados com sucesso!")
