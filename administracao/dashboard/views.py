from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from agendamentos.models import Agendamento
from salas.models import Sala
from administracao.models import Perfil
from datetime import datetime
from django.db.models import Count, Q


@login_required
def dashboard(request):
    """
    Dashboard diferenciado por tipo de perfil:
    - PROFESSOR: Vê seus próprios agendamentos e estatísticas pessoais
    - COORDENADOR: Vê solicitações pendentes + estatísticas gerais
    - ADMIN: Vê tudo + gerenciamento de usuários e salas
    """
    try:
        perfil = request.user.perfil
    except Perfil.DoesNotExist:
        messages.error(request, 'Perfil não configurado. Entre em contato com o administrador.')
        return redirect('usuarios:perfil')
    
    hoje = datetime.now().date()
    
    # ========================================================================
    # DADOS COMUNS (todos os perfis)
    # ========================================================================
    
    # Contadores de agendamentos DO USUÁRIO
    meus_agendamentos_total = Agendamento.objects.filter(usuario=request.user).count()
    meus_agendamentos_aprovados = Agendamento.objects.filter(usuario=request.user, status='A').count()
    meus_agendamentos_pendentes = Agendamento.objects.filter(usuario=request.user, status='P').count()
    meus_agendamentos_reprovados = Agendamento.objects.filter(usuario=request.user, status='R').count()
    
    # Próximos agendamentos do usuário (futuros e aprovados)
    meus_proximos_agendamentos = Agendamento.objects.filter(
        usuario=request.user, 
        status='A',
        data__gte=hoje
    ).select_related('sala').order_by('data', 'horario_inicio')[:5]
    
    # ========================================================================
    # DADOS ESPECÍFICOS POR PERFIL
    # ========================================================================
    
    context = {
        'perfil': perfil,
        'meus_agendamentos_total': meus_agendamentos_total,
        'meus_agendamentos_aprovados': meus_agendamentos_aprovados,
        'meus_agendamentos_pendentes': meus_agendamentos_pendentes,
        'meus_agendamentos_reprovados': meus_agendamentos_reprovados,
        'meus_proximos_agendamentos': meus_proximos_agendamentos,
    }
    
    # COORDENADOR e ADMIN - dados globais
    if perfil.tipo in ['COO', 'ADM']:
        # Total de solicitações pendentes (TODOS os usuários)
        total_solicitacoes_pendentes = Agendamento.objects.filter(status='P').count()
        
        # Estatísticas gerais
        total_agendamentos_sistema = Agendamento.objects.count()
        total_aprovados_sistema = Agendamento.objects.filter(status='A').count()
        total_reprovados_sistema = Agendamento.objects.filter(status='R').count()
        
        # Salas mais utilizadas (com agendamentos APROVADOS)
        salas_mais_utilizadas = Sala.objects.annotate(
            total_agendamentos=Count('agendamentos', filter=Q(agendamentos__status='A'))
        ).order_by('-total_agendamentos')[:5]
        
        salas_nomes = [sala.nome for sala in salas_mais_utilizadas]
        salas_counts = [sala.total_agendamentos for sala in salas_mais_utilizadas]
        
        # Agendamentos recentes (todos os usuários)
        agendamentos_recentes = Agendamento.objects.all().select_related(
            'usuario', 'sala'
        ).order_by('-criado_em')[:10]
        
        context.update({
            'total_solicitacoes_pendentes': total_solicitacoes_pendentes,
            'total_agendamentos_sistema': total_agendamentos_sistema,
            'total_aprovados_sistema': total_aprovados_sistema,
            'total_reprovados_sistema': total_reprovados_sistema,
            'salas_nomes': salas_nomes,
            'salas_counts': salas_counts,
            'agendamentos_recentes': agendamentos_recentes,
        })
    
    # APENAS ADMIN - dados de gerenciamento
    if perfil.tipo == 'ADM':
        total_usuarios = User.objects.count()
        total_salas = Sala.objects.count()
        total_professores = Perfil.objects.filter(tipo='PRO').count()
        total_coordenadores = Perfil.objects.filter(tipo='COO').count()
        total_admins = Perfil.objects.filter(tipo='ADM').count()
        
        context.update({
            'total_usuarios': total_usuarios,
            'total_salas': total_salas,
            'total_professores': total_professores,
            'total_coordenadores': total_coordenadores,
            'total_admins': total_admins,
        })
    
    return render(request, 'dashboard/dashboard.html', context)
