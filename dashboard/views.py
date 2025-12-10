from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from agendamentos.models import Agendamento


@login_required
def dashboard(request):
    """Dashboard com estatísticas e próximos agendamentos"""
    
    # Dados para estatísticas
    total_agendamentos = Agendamento.objects.filter(usuario=request.user).count()
    agendamentos_aprovados = Agendamento.objects.filter(
        usuario=request.user, 
        status='Aprovado'
    ).count()
    agendamentos_pendentes = Agendamento.objects.filter(
        usuario=request.user, 
        status='Pendente'
    ).count()
    agendamentos_rejeitados = Agendamento.objects.filter(
        usuario=request.user, 
        status='Rejeitado'
    ).count()
    
    # Próximos agendamentos (aprovados)
    proximos_agendamentos = Agendamento.objects.filter(
        usuario=request.user,
        status='Aprovado'
    ).order_by('data', 'horario_inicio')[:5]
    
    # Solicitações pendentes (apenas para coordenadores)
    solicitacoes_pendentes = []
    if request.user.groups.filter(name='Coordenacao').exists():
        solicitacoes_pendentes = Agendamento.objects.filter(
            status='Pendente'
        ).order_by('-data')[:5]
    
    # Histórico de agendamentos
    historico_agendamentos = Agendamento.objects.filter(
        usuario=request.user
    ).order_by('-data')[:10]
    
    context = {
        'total_agendamentos': total_agendamentos,
        'agendamentos_aprovados': agendamentos_aprovados,
        'agendamentos_pendentes': agendamentos_pendentes,
        'agendamentos_rejeitados': agendamentos_rejeitados,
        'proximos_agendamentos': proximos_agendamentos,
        'solicitacoes_pendentes': solicitacoes_pendentes,
        'historico_agendamentos': historico_agendamentos,
    }
    
    return render(request, 'dashboard.html', context)
