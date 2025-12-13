#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'administracao.settings')
django.setup()

from django.contrib.auth.models import User
from administracao.models import Perfil

usuarios = User.objects.all()
for user in usuarios:
    try:
        perfil = user.perfil
        print(f"{user.username}: {perfil.tipo}")
    except Perfil.DoesNotExist:
        print(f"{user.username}: SEM PERFIL")
