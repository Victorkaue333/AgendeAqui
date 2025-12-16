from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.db.models import Q
from django.http import JsonResponse
from datetime import datetime
import threading

from .models import Agendamento
from .forms import AgendamentoCreateForm, AgendamentoApprovalForm
from salas.models import Sala
from administracao.models import Perfil


def _enqueue_booking_notification(agendamento_id, event):
    """Dispara a notificação em background para não atrasar a resposta HTTP."""

    def _run():
        try:
            from .tasks import send_booking_notification_async
            send_booking_notification_async.delay(agendamento_id, event)
        except Exception:
            # Se o broker do Celery estiver fora, não bloquear a UX
            pass

    threading.Thread(target=_run, daemon=True).start()


def _create_in_app_notification(usuario, *, titulo: str, mensagem: str, nivel: str = 'info', url: str = ''):
    """Cria notificação in-app para o usuário sem quebrar o fluxo em caso de erro."""

    try:
        from notificacoes.models import Notificacao

        Notificacao.objects.create(
            usuario=usuario,
            titulo=titulo,
            mensagem=mensagem,
            nivel=nivel,
            url=url,
        )
    except Exception:
        # Fail-safe: não bloquear aprovação/reprovação
        pass


# ============================================================================
# DECORADORES E MIXINS PARA CONTROLE DE ACESSO
# ============================================================================

def coordenador_required(func):
    """Decorator para garantir que apenas coordenadores acessem a view."""
    def wrapper(request, *args, **kwargs):
        try:
            perfil = request.user.perfil
            if perfil.tipo not in ['COO', 'ADM']:
                messages.error(request, 'Você não tem permissão para acessar esta página.')
                return HttpResponseRedirect(reverse('acesso_rapido'))
        except Perfil.DoesNotExist:
            messages.error(request, 'Perfil não encontrado.')
            return HttpResponseRedirect(reverse('acesso_rapido'))
        
        return func(request, *args, **kwargs)
    return wrapper


class CoordenadorRequiredMixin(UserPassesTestMixin, LoginRequiredMixin):
    """Mixin para garantir que apenas coordenadores acessem a view."""
    def test_func(self):
        try:
            perfil = self.request.user.perfil
            return perfil.tipo in ['COO', 'ADM']
        except Perfil.DoesNotExist:
            return False
    
    def handle_no_permission(self):
        messages.error(self.request, 'Você não tem permissão para acessar esta página.')
        return HttpResponseRedirect(reverse('acesso_rapido'))


# ============================================================================
# VIEWS PÚBLICAS
# ============================================================================

@login_required
def calendario(request):
    """
    View do calendário interativo - FullCalendar.
    
    ADMIN/COORDENADOR: Vê TODOS os agendamentos
    PROFESSOR: Vê só os agendamentos aprovados (para consultar disponibilidade)
    """
    try:
        perfil = request.user.perfil
    except Perfil.DoesNotExist:
        messages.error(request, 'Perfil não configurado.')
        return HttpResponseRedirect(reverse('usuarios:perfil'))

    salas = Sala.objects.all()
    
    # Contar pendentes para o badge
    agendamentos_pendentes = 0
    if perfil.tipo in ['COO', 'ADM']:
        agendamentos_pendentes = Agendamento.objects.filter(status='P').count()

    context = {
        'salas': salas,
        'perfil': perfil,
        'agendamentos_pendentes': agendamentos_pendentes,
    }
    
    return render(request, 'agendamentos/calendario.html', context)


@login_required
def agendamentos(request):
    """
    View principal de agendamentos - Lista em tabela.
    
    ADMIN/COORDENADOR: Vê TODOS os agendamentos
    PROFESSOR: Vê só os agendamentos aprovados (para consultar disponibilidade)
    """
    try:
        perfil = request.user.perfil
    except Perfil.DoesNotExist:
        messages.error(request, 'Perfil não configurado.')
        return HttpResponseRedirect(reverse('usuarios:perfil'))

    salas = Sala.objects.all()
    
    # Filtros opcionais
    sala_id = request.GET.get('sala')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    status_filter = request.GET.get('status')
    
    # Definir queryset conforme permissão
    if perfil.tipo in ['COO', 'ADM']:
        # Admin/Coordenador: VÊ TODOS OS AGENDAMENTOS
        agendamentos_list = Agendamento.objects.all().select_related('sala', 'usuario')
    else:
        # Professor: VÊ SEUS PRÓPRIOS agendamentos (todos status) + APROVADOS dos outros
        agendamentos_list = Agendamento.objects.filter(
            Q(usuario=request.user) | Q(status='A')
        ).select_related('sala', 'usuario')
    
    # Aplicar filtros
    if sala_id:
        agendamentos_list = agendamentos_list.filter(sala_id=sala_id)
    
    if data_inicio:
        agendamentos_list = agendamentos_list.filter(data__gte=data_inicio)
    
    if data_fim:
        agendamentos_list = agendamentos_list.filter(data__lte=data_fim)
    
    # Para admin/coordenador: filtrar por status
    if perfil.tipo in ['COO', 'ADM'] and status_filter:
        agendamentos_list = agendamentos_list.filter(status=status_filter)
    
    # Ordenar por data e horário
    agendamentos_list = agendamentos_list.order_by('data', 'horario_inicio')
    
    # Estatísticas
    agendamentos_total = agendamentos_list.count()
    agendamentos_aprovados = agendamentos_list.filter(status='A').count()
    agendamentos_pendentes = agendamentos_list.filter(status='P').count()
    agendamentos_rejeitados = agendamentos_list.filter(status='R').count()

    context = {
        'salas': salas,
        'agendamentos': agendamentos_list,
        'perfil': perfil,
        # Estatísticas
        'agendamentos_total': agendamentos_total,
        'agendamentos_aprovados': agendamentos_aprovados,
        'agendamentos_pendentes': agendamentos_pendentes,
        'agendamentos_rejeitados': agendamentos_rejeitados,
        # Filtros (para manter valores nos inputs)
        'sala_id_filter': sala_id,
        'data_inicio_filter': data_inicio,
        'data_fim_filter': data_fim,
        'status_filter': status_filter,
    }
    
    return render(request, 'agendamentos/agendamentos.html', context)


# ============================================================================
# CRUD DE AGENDAMENTOS (PROFESSOR)
# ============================================================================

class AgendamentoCreateView(LoginRequiredMixin, CreateView):
    """
    View para criar (solicitar) um novo agendamento.
    Usuário logado (Professor) pode solicitar reservas.
    """
    model = Agendamento
    form_class = AgendamentoCreateForm
    template_name = 'agendamentos/form.html'
    success_url = reverse_lazy('agendamentos:agendamentos')

    def form_valid(self, form):
        """Associar o usuário logado ao agendamento."""
        try:
            agendamento = form.save(commit=False)
            agendamento.usuario = self.request.user
            agendamento.status = 'P'  # Pendente
            agendamento.save()
            
            # Adicionar flag de sucesso na sessão para mostrar modal
            self.request.session['agendamento_criado'] = True
            self.request.session['agendamento_id'] = agendamento.id
            
            from django.http import HttpResponseRedirect
            from django.urls import reverse
            return HttpResponseRedirect(reverse('agendamentos:agendamentos'))
        except Exception as e:
            messages.error(self.request, f'Erro ao criar agendamento: {str(e)}')
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['acao'] = 'Solicitar Agendamento'
        return context


class AgendamentoDetailView(LoginRequiredMixin, DetailView):
    """
    Visualizar detalhes de um agendamento específico.
    """
    model = Agendamento
    template_name = 'agendamentos/detail.html'
    context_object_name = 'agendamento'

    def get_object(self):
        obj = super().get_object()
        # Apenas o próprio usuário ou coordenador pode ver
        if self.request.user != obj.usuario:
            try:
                perfil = self.request.user.perfil
                if perfil.tipo not in ['COO', 'ADM']:
                    messages.error(self.request, 'Sem permissão.')
                    return None
            except Perfil.DoesNotExist:
                messages.error(self.request, 'Perfil não encontrado.')
                return None
        return obj


# ============================================================================
# GESTÃO DE AGENDAMENTOS (COORDENADOR)
# ============================================================================

class AgendamentoPendentesListView(CoordenadorRequiredMixin, ListView):
    """
    Lista todos os agendamentos PENDENTES de aprovação.
    Apenas coordenadores podem acessar.
    """
    model = Agendamento
    template_name = 'agendamentos/pendentes.html'
    context_object_name = 'agendamentos'
    paginate_by = 20

    def get_queryset(self):
        return Agendamento.objects.filter(
            status='P'
        ).select_related('usuario', 'sala').order_by('data', 'horario_inicio')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_pendentes'] = self.get_queryset().count()
        return context


class AgendamentoApproveView(CoordenadorRequiredMixin, DetailView):
    """
    Aprovar ou reprovar um agendamento pendente.
    """
    model = Agendamento
    template_name = 'agendamentos/approve.html'
    context_object_name = 'agendamento'

    def get_queryset(self):
        """Apenas agendamentos pendentes podem ser aprovados."""
        return Agendamento.objects.filter(status='P')
    
    def get(self, request, *args, **kwargs):
        """Verificar se o agendamento existe e está pendente."""
        try:
            self.object = self.get_object()
            return super().get(request, *args, **kwargs)
        except:
            messages.error(request, '❌ Este agendamento não está mais pendente ou não existe.')
            return HttpResponseRedirect(reverse('agendamentos:agendamentos'))

    def post(self, request, *args, **kwargs):
        """Processar aprovação ou reprovação."""
        try:
            agendamento = self.get_object()
        except:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Este agendamento não está mais pendente ou não existe.'
                })
            messages.error(request, '❌ Este agendamento não está mais pendente ou não existe.')
            return HttpResponseRedirect(reverse('agendamentos:agendamentos'))
        
        # Determinar ação
        acao = request.POST.get('acao')
        
        if acao == 'A':
            # Aprovar
            agendamento.status = 'A'
            agendamento.justificativa_reprovacao = ''
            agendamento.save()

            _create_in_app_notification(
                agendamento.usuario,
                titulo='Agendamento aprovado',
                mensagem=f'Seu agendamento #{agendamento.id} foi aprovado.',
                nivel='success',
                url=reverse('agendamentos:detail', args=[agendamento.id]),
            )
            
            # Enfileirar notificação em background (não bloquear)
            _enqueue_booking_notification(agendamento.id, 'approved')
            
            # Retornar JSON imediatamente se for AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Agendamento #{agendamento.id} aprovado!',
                    'status': 'aprovado'
                })
            
            messages.success(request, f'✅ Agendamento #{agendamento.id} aprovado com sucesso!')
            
        elif acao == 'R':
            # Reprovar
            justificativa = request.POST.get('justificativa_reprovacao', '').strip()
            
            if not justificativa:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': 'A justificativa é obrigatória para reprovar.'
                    })
                messages.error(request, '❌ A justificativa é obrigatória para reprovar um agendamento.')
                return HttpResponseRedirect(request.path)
            
            agendamento.status = 'R'
            agendamento.justificativa_reprovacao = justificativa
            agendamento.save()

            _create_in_app_notification(
                agendamento.usuario,
                titulo='Agendamento reprovado',
                mensagem=f'Seu agendamento #{agendamento.id} foi reprovado. Justificativa: {justificativa}',
                nivel='danger',
                url=reverse('agendamentos:detail', args=[agendamento.id]),
            )
            
            # Enfileirar notificação em background (não bloquear)
            _enqueue_booking_notification(agendamento.id, 'rejected')
            
            # Retornar JSON imediatamente se for AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Agendamento #{agendamento.id} reprovado.',
                    'status': 'reprovado'
                })
            
            messages.success(request, f'❌ Agendamento #{agendamento.id} reprovado.')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': '❌ Ação inválida. Selecione Aprovar ou Reprovar.'
                })
            messages.error(request, '❌ Ação inválida. Selecione Aprovar ou Reprovar.')
            return HttpResponseRedirect(request.path)
        
        return HttpResponseRedirect(reverse('agendamentos:agendamentos'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        agendamento = self.object
        context['usuario_nome'] = agendamento.usuario.get_full_name() or agendamento.usuario.username
        context['sala_nome'] = agendamento.sala.nome
        return context


# ============================================================================
# VIEWS ADICIONAIS
# ============================================================================

@login_required
@coordenador_required
def agendamentos_aprovados(request):
    """
    Lista todos os agendamentos APROVADOS.
    Apenas coordenadores podem acessar.
    """
    agendamentos = Agendamento.objects.filter(
        status='A'
    ).select_related('usuario', 'sala').order_by('data', 'horario_inicio')

    # Filtros opcionais
    sala_id = request.GET.get('sala')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')

    if sala_id:
        agendamentos = agendamentos.filter(sala_id=sala_id)
    if data_inicio:
        agendamentos = agendamentos.filter(data__gte=data_inicio)
    if data_fim:
        agendamentos = agendamentos.filter(data__lte=data_fim)

    salas = Sala.objects.all()

    context = {
        'agendamentos': agendamentos,
        'salas': salas,
        'total_aprovados': agendamentos.count(),
    }
    return render(request, 'agendamentos/aprovados.html', context)


@login_required
def meus_agendamentos(request):
    """
    Lista os agendamentos do usuário logado.
    Cada um pode ver seus próprios agendamentos.
    """
    agendamentos = Agendamento.objects.filter(
        usuario=request.user
    ).select_related('sala').order_by('-data', '-atualizado_em')

    # Filtro por status
    status_filter = request.GET.get('status')
    if status_filter in ['P', 'A', 'R']:
        agendamentos = agendamentos.filter(status=status_filter)

    context = {
        'agendamentos': agendamentos,
        'total': agendamentos.count(),
    }
    return render(request, 'agendamentos/meus_agendamentos.html', context)


@login_required
def cancelar_agendamento(request, pk):
    """
    Cancela um agendamento.
    Apenas o usuário criador pode cancelar.
    """
    agendamento = get_object_or_404(Agendamento, pk=pk)
    
    # Verificar permissão
    if agendamento.usuario != request.user:
        messages.error(request, 'Você não tem permissão para cancelar este agendamento.')
        return HttpResponseRedirect(reverse('agendamentos:meus_agendamentos'))
    
    # Verificar se já foi reprovado
    if agendamento.status == 'R':
        messages.error(request, 'Este agendamento já foi reprovado/cancelado.')
        return HttpResponseRedirect(reverse('agendamentos:meus_agendamentos'))
    
    if request.method == 'POST':
        motivo = request.POST.get('motivo', '').strip()
        
        # Verificar se pode cancelar
        if not agendamento.pode_cancelar():
            messages.error(
                request, 
                'Não é possível cancelar este agendamento. O cancelamento deve ser feito com pelo menos 24 horas de antecedência.'
            )
            return HttpResponseRedirect(reverse('agendamentos:meus_agendamentos'))
        
        try:
            agendamento.cancelar(motivo)
            messages.success(request, 'Agendamento cancelado com sucesso!')
            return HttpResponseRedirect(reverse('agendamentos:meus_agendamentos'))
        except Exception as e:
            messages.error(request, f'Erro ao cancelar agendamento: {str(e)}')
            return HttpResponseRedirect(reverse('agendamentos:meus_agendamentos'))
    
    context = {
        'agendamento': agendamento,
    }
    return render(request, 'agendamentos/cancelar.html', context)


# ============================================================================
# API JSON PARA CALENDÁRIO
# ============================================================================

@login_required
def agendamentos_json(request):
    """
    Retorna agendamentos em formato JSON para o FullCalendar.
    
    ADMIN/COORDENADOR: Vê todos os agendamentos
    PROFESSOR: Vê apenas os aprovados (para consultar disponibilidade)
    """
    try:
        perfil = request.user.perfil
    except Perfil.DoesNotExist:
        return JsonResponse({'error': 'Perfil não configurado'}, status=403)
    
    # Filtros da URL
    sala_id = request.GET.get('sala')
    start = request.GET.get('start')  # Data início (ISO format)
    end = request.GET.get('end')      # Data fim (ISO format)
    
    # Definir queryset conforme permissão
    if perfil.tipo in ['COO', 'ADM']:
        agendamentos_qs = Agendamento.objects.all()
    else:
        agendamentos_qs = Agendamento.objects.filter(status='A')
    
    # Aplicar filtros
    if sala_id:
        agendamentos_qs = agendamentos_qs.filter(sala_id=sala_id)
    
    if start:
        agendamentos_qs = agendamentos_qs.filter(data__gte=start)
    
    if end:
        agendamentos_qs = agendamentos_qs.filter(data__lte=end)
    
    # Selecionar dados relacionados
    agendamentos_qs = agendamentos_qs.select_related('sala', 'usuario', 'usuario__perfil')
    
    # Montar eventos para o FullCalendar
    eventos = []
    for ag in agendamentos_qs:
        # Definir cor por status
        color_map = {
            'P': '#f59e0b',  # Pendente - Amarelo/Laranja
            'A': '#10b981',  # Aprovado - Verde
            'R': '#ef4444',  # Reprovado - Vermelho
        }
        
        # Combinar data + horários
        start_datetime = f"{ag.data}T{ag.horario_inicio}"
        end_datetime = f"{ag.data}T{ag.horario_fim}"
        
        # Nome do usuário
        usuario_nome = ag.usuario.get_full_name() or ag.usuario.username
        
        # Título do evento
        titulo = f"{ag.sala.nome} - {usuario_nome}"
        
        # Adicionar status para coordenador
        if perfil.tipo in ['COO', 'ADM']:
            status_texto = ag.get_status_display()
            titulo = f"[{status_texto}] {titulo}"
        
        eventos.append({
            'id': ag.id,
            'title': titulo,
            'start': start_datetime,
            'end': end_datetime,
            'color': color_map.get(ag.status, '#6366f1'),
            'extendedProps': {
                'sala': ag.sala.nome,
                'usuario': usuario_nome,
                'status': ag.status,
                'status_display': ag.get_status_display(),
                'descricao': ag.descricao or '',
                'url': f"/agendamentos/{ag.id}/",
            }
        })
    
    return JsonResponse(eventos, safe=False)
