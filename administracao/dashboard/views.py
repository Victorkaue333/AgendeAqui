from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from agendamentos.models import Agendamento
from salas.models import Sala, Bloco
from datetime import datetime, timedelta
from django.db.models import Count, Q

@login_required
def dashboard(request):
    # Contadores de agendamentos
    total_agendamentos = Agendamento.objects.filter(usuario=request.user).count()
    agendamentos_aprovados = Agendamento.objects.filter(usuario=request.user, status='A').count()
    agendamentos_pendentes = Agendamento.objects.filter(usuario=request.user, status='P').count()
    agendamentos_rejeitados = Agendamento.objects.filter(usuario=request.user, status='R').count()
    
    # Próximos agendamentos (futuros e aprovados)
    hoje = datetime.now().date()
    proximos_agendamentos = Agendamento.objects.filter(
        usuario=request.user, 
        status='A',
        data__gte=hoje
    ).select_related('sala').order_by('data', 'horario_inicio')[:5]
    
    # Solicitações pendentes (para coordenadores)
    solicitacoes_pendentes = 0
    if request.user.groups.filter(name='Coordenacao').exists():
        solicitacoes_pendentes = Agendamento.objects.filter(status='P').count()
    
    # Histórico de atividades (últimos 10 agendamentos do usuário)
    historico_agendamentos = Agendamento.objects.filter(
        usuario=request.user
    ).select_related('sala').order_by('-data', '-atualizado_em')[:10]
    
    # Dados para os gráficos
    # Salas mais utilizadas
    salas_mais_utilizadas = Sala.objects.annotate(
        total_agendamentos=Count('agendamentos')
    ).order_by('-total_agendamentos')[:5]
    
    salas_nomes = [sala.nome for sala in salas_mais_utilizadas]
    salas_counts = [sala.total_agendamentos for sala in salas_mais_utilizadas]
    
    # Total de salas
    total_salas = Sala.objects.count()
    
    # Total de usuários com agendamentos
    usuarios_com_agendamentos = User.objects.filter(
        agendamentos__isnull=False
    ).distinct().count()
    
    context = {
        'total_agendamentos': total_agendamentos,
        'agendamentos_aprovados': agendamentos_aprovados,
        'agendamentos_pendentes': agendamentos_pendentes,
        'agendamentos_rejeitados': agendamentos_rejeitados,
        'proximos_agendamentos': proximos_agendamentos,
        'solicitacoes_pendentes': solicitacoes_pendentes,
        'historico_agendamentos': historico_agendamentos,
        'total_salas': total_salas,
        'usuarios_com_agendamentos': usuarios_com_agendamentos,
        'salas_nomes': salas_nomes,
        'salas_counts': salas_counts,
    }
    
    return render(request, 'dashboard/dashboard.html', context)
