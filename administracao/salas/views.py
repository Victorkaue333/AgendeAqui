from django.urls import reverse_lazy
from django.views import generic
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from datetime import datetime
from .models import Sala


class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin para garantir que apenas administradores acessem a view."""
    def test_func(self):
        try:
            return self.request.user.perfil.tipo == 'ADM'
        except:
            return False
    
    def handle_no_permission(self):
        from django.http import HttpResponseRedirect
        from django.urls import reverse
        messages.error(self.request, 'Acesso negado. Apenas administradores podem gerenciar salas.')
        return HttpResponseRedirect(reverse('salas:list'))


class SalaListView(LoginRequiredMixin, generic.ListView):
    """Todos podem visualizar salas"""
    model = Sala
    template_name = 'salas/list.html'
    context_object_name = 'salas'


class SalaCreateView(AdminRequiredMixin, LoginRequiredMixin, generic.CreateView):
    """Apenas Admin pode criar salas"""
    model = Sala
    form_class = None  # Será importado abaixo
    template_name = 'salas/form.html'
    success_url = reverse_lazy('salas:list')
    
    def get_form_class(self):
        from .forms import SalaForm
        return SalaForm
    
    def form_valid(self, form):
        from django.http import HttpResponseRedirect
        from django.urls import reverse
        
        sala = form.save()
        messages.success(self.request, f'Sala "{sala.nome}" criada com sucesso!')
        return HttpResponseRedirect(reverse('salas:list'))


class SalaUpdateView(AdminRequiredMixin, LoginRequiredMixin, generic.UpdateView):
    """Apenas Admin pode editar salas"""
    model = Sala
    form_class = None  # Será importado abaixo
    template_name = 'salas/form.html'
    success_url = reverse_lazy('salas:list')
    
    def get_form_class(self):
        from .forms import SalaForm
        return SalaForm
    
    def form_valid(self, form):
        from django.http import JsonResponse
        sala = form.save()
        
        # Se for requisição AJAX, retornar JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest' or self.request.headers.get('X-CSRFToken'):
            return JsonResponse({
                'success': True,
                'message': f'Sala "{sala.nome}" atualizada com sucesso!',
                'sala': {
                    'id': sala.id,
                    'nome': sala.nome,
                    'capacidade': sala.capacidade,
                    'bloco': sala.get_bloco_display(),
                    'recursos': [r.nome for r in sala.recursos.all()]
                }
            })
        
        messages.success(self.request, f'Sala "{sala.nome}" atualizada com sucesso!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        from django.http import JsonResponse
        # Se for AJAX, retornar erros em JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest' or self.request.headers.get('X-CSRFToken'):
            errors = {}
            for field, error_list in form.errors.items():
                errors[field] = error_list[0]
            return JsonResponse({
                'success': False,
                'errors': errors
            })
        return super().form_invalid(form)


class SalaDeleteView(AdminRequiredMixin, LoginRequiredMixin, generic.DeleteView):
    """Apenas Admin pode excluir salas"""
    model = Sala
    template_name = 'salas/confirm_delete.html'
    success_url = reverse_lazy('salas:list')
    
    def delete(self, request, *args, **kwargs):
        """Validar exclusão de sala com agendamentos ativos"""
        sala = self.get_object()
        hoje = datetime.now().date()
        
        # Verificar se há agendamentos futuros aprovados
        agendamentos_futuros = sala.agendamentos.filter(
            Q(status='A') | Q(status='P'),
            data__gte=hoje
        ).count()
        
        if agendamentos_futuros > 0:
            from django.http import HttpResponseRedirect
            from django.urls import reverse
            messages.error(
                request,
                f'Não é possível excluir a sala "{sala.nome}" pois ela possui {agendamentos_futuros} agendamento(s) futuro(s).'
            )
            return HttpResponseRedirect(reverse('salas:list'))
        
        messages.success(request, f'Sala "{sala.nome}" excluída com sucesso!')
        return super().delete(request, *args, **kwargs)


class SalaDetailView(generic.DetailView):
    """
    Visualiza detalhes de uma sala e seus agendamentos.
    """
    model = Sala
    template_name = 'salas/detail.html'
    context_object_name = 'sala'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sala = self.object
        hoje = datetime.now().date()
        
        # Filtros
        status_filter = self.request.GET.get('status')
        data_inicio = self.request.GET.get('data_inicio')
        data_fim = self.request.GET.get('data_fim')
        
        # Agendamentos da sala
        agendamentos = sala.agendamentos.all().select_related('usuario').order_by('-data', 'horario_inicio')
        
        # Aplicar filtros
        if status_filter:
            agendamentos = agendamentos.filter(status=status_filter)
        if data_inicio:
            agendamentos = agendamentos.filter(data__gte=data_inicio)
        if data_fim:
            agendamentos = agendamentos.filter(data__lte=data_fim)
        
        # Estatísticas
        context['total_agendamentos'] = sala.agendamentos.count()
        context['agendamentos_aprovados'] = sala.agendamentos.filter(status='A').count()
        context['agendamentos_pendentes'] = sala.agendamentos.filter(status='P').count()
        context['agendamentos_futuros'] = sala.agendamentos.filter(
            Q(status='A') | Q(status='P'),
            data__gte=hoje
        ).count()
        
        # Lista de agendamentos
        context['agendamentos'] = agendamentos[:50]  # Limitar a 50
        
        # Filtros para o template
        context['status_filter'] = status_filter
        context['data_inicio_filter'] = data_inicio
        context['data_fim_filter'] = data_fim
        
        # Recursos da sala
        context['recursos'] = sala.recursos.all()
        
        return context
