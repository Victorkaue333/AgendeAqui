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
        print(f"{user.username} já tem perfil: {perfil.tipo}")
    except Perfil.DoesNotExist:
        # Se for admin, criar com tipo ADM
        if user.is_superuser:
            tipo = 'ADM'
        else:
            tipo = 'PRO'
        
        perfil = Perfil.objects.create(usuario=user, tipo=tipo)
        print(f"✓ Perfil criado para {user.username} com tipo {tipo}")
