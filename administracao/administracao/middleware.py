"""
Middleware para controle de acesso baseado em perfis de usuário.
"""
from django.shortcuts import redirect
from django.contrib import messages
from administracao.models import Perfil
import re


class PerfilAccessMiddleware:
    """
    Middleware que controla o acesso às URLs baseado no perfil do usuário.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Mapeamento de URLs e perfis permitidos (ordem importa - mais específico primeiro)
        self.access_rules = [
            # Admin only - Usuários
            (r'^/usuarios/usuarios/', ['ADM']),
            (r'^/usuarios/.+/editar-perfil/', ['ADM']),
            (r'^/usuarios/.+/redefinir-senha/', ['ADM']),
            (r'^/usuarios/.+/excluir/', ['ADM']),
            (r'^/usuarios/.+/detalhes/', ['ADM']),
            (r'^/usuarios/criar/', ['ADM']),
            
            # Admin only - Salas
            (r'^/salas/create/', ['ADM']),
            (r'^/salas/\d+/edit/', ['ADM']),
            (r'^/salas/\d+/delete/', ['ADM']),
            
            # Admin e Coordenador - Agendamentos
            (r'^/agendamentos/pendentes/', ['ADM', 'COO']),
            (r'^/agendamentos/\d+/aprovar/', ['ADM', 'COO']),
            (r'^/agendamentos/aprovados/', ['ADM', 'COO']),
            
            # Admin e Coordenador - Relatórios
            (r'^/relatorios/', ['ADM', 'COO']),
        ]
    
    def __call__(self, request):
        """Processa a requisição"""
        # Ignorar se não estiver autenticado
        if not request.user.is_authenticated:
            return self.get_response(request)
        
        # Ignorar rotas públicas
        if request.path.startswith(('/login', '/logout', '/cadastro', '/static', '/media', '/admin', '/acesso-rapido')):
            return self.get_response(request)
        
        # Verificar se usuário tem perfil
        try:
            perfil = request.user.perfil
        except (Perfil.DoesNotExist, AttributeError):
            messages.error(request, 'Perfil não configurado. Entre em contato com o administrador.')
            return redirect('login')
        
        # Verificar acesso específico por URL
        for url_pattern, allowed_profiles in self.access_rules:
            if re.match(url_pattern, request.path):
                if perfil.tipo not in allowed_profiles:
                    messages.error(
                        request, 
                        f'⛔ Acesso negado. Esta funcionalidade é restrita a: {", ".join(allowed_profiles)}'
                    )
                    return redirect('dashboard:home')
        
        # Continuar processamento normal
        return self.get_response(request)
