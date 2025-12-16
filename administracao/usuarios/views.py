from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from agendamentos.models import Agendamento
from administracao.models import Perfil, AuditLog
from .forms import UserRegistrationForm, AlterarPerfilForm, CriarUsuarioForm
import secrets


# ============================================================================
# DECORADORES PARA CONTROLE DE ACESSO
# ============================================================================

def admin_required(func):
    """Decorator para garantir que apenas admins acessem a view"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Você precisa estar logado.')
            return redirect('login')
        try:
            perfil = request.user.perfil
            if perfil.tipo != 'ADM':
                messages.error(request, 'Acesso restrito a Administradores.')
                return redirect('acesso_rapido')
        except Perfil.DoesNotExist:
            messages.error(request, 'Perfil não encontrado.')
            return redirect('acesso_rapido')
        return func(request, *args, **kwargs)
    return wrapper


# ============================================================================
# VIEWS EXISTENTES (mantidas)
# ============================================================================

def cadastro(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data.get('email')
            user.save()
            messages.success(request, 'Cadastro realizado com sucesso! Faça login.')
            return redirect('login')
        else:
            messages.error(request, 'Verifique os dados informados.')
    else:
        form = UserRegistrationForm()

    return render(request, 'cadastro.html', {'form': form})


@login_required
def perfil(request):
    """Visualizar e editar perfil do usuário"""
    
    # Histórico de agendamentos
    historico_agendamentos = Agendamento.objects.filter(
        usuario=request.user
    ).order_by('-data')
    
    if request.method == 'POST':
        action = request.POST.get('action', 'update')
        
        if action == 'change_password':
            # Mudar senha
            old_password = request.POST.get('old_password', '')
            new_password1 = request.POST.get('new_password1', '')
            new_password2 = request.POST.get('new_password2', '')
            
            if request.user.check_password(old_password):
                if new_password1 == new_password2:
                    request.user.set_password(new_password1)
                    request.user.save()
                    messages.success(request, 'Senha alterada com sucesso!')
                else:
                    messages.error(request, 'As senhas não coincidem.')
            else:
                messages.error(request, 'Senha atual incorreta.')
        else:
            # Atualizar dados pessoais (ação padrão)
            request.user.first_name = request.POST.get('first_name', '')
            request.user.last_name = request.POST.get('last_name', '')
            request.user.email = request.POST.get('email', '')
            request.user.save()
            messages.success(request, 'Dados atualizados com sucesso!')
        
        return redirect('usuarios:perfil')
    
    context = {
        'historico_agendamentos': historico_agendamentos,
    }
    
    return render(request, 'perfil.html', context)


# ============================================================================
# NOVAS VIEWS PARA GERENCIAMENTO DE USUÁRIOS (ADMIN ONLY)
# ============================================================================

class UsuariosListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    Lista todos os usuários do sistema.
    Acessível apenas para Administrador.
    """
    model = User
    template_name = 'usuarios/usuarios_list.html'
    context_object_name = 'usuarios'
    paginate_by = 10
    
    def test_func(self):
        try:
            return self.request.user.perfil.tipo == 'ADM'
        except Perfil.DoesNotExist:
            return False
    
    def get_queryset(self):
        queryset = User.objects.all().select_related('perfil').order_by('-date_joined')
        
        # Filtro por tipo
        tipo = self.request.GET.get('tipo')
        if tipo:
            queryset = queryset.filter(perfil__tipo=tipo)
        
        # Busca por nome ou email
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(first_name__icontains=q) | 
                Q(last_name__icontains=q) | 
                Q(email__icontains=q)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipo_choices'] = Perfil.PERFIL_CHOICES
        context['tipo_filter'] = self.request.GET.get('tipo', '')
        context['q'] = self.request.GET.get('q', '')
        return context


@login_required
@admin_required
def criar_usuario(request):
    """
    Cria um novo usuário (padrão: Professor).
    Gera senha temporária e envia por email.
    """
    if request.method == 'POST':
        form = CriarUsuarioForm(request.POST)
        if form.is_valid():
            # Gerar username baseado no email
            email = form.cleaned_data['email']
            username = email.split('@')[0]
            
            # Garantir username único
            counter = 1
            original_username = username
            while User.objects.filter(username=username).exists():
                username = f"{original_username}{counter}"
                counter += 1
            
            # Gerar senha temporária
            senha_temporaria = secrets.token_urlsafe(12)[:12]
            
            # Criar usuário
            user = User.objects.create_user(
                username=username,
                email=email,
                password=senha_temporaria,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name']
            )
            
            # Criar perfil
            tipo = form.cleaned_data.get('tipo', 'PRO')
            perfil = Perfil.objects.create(
                usuario=user,
                tipo=tipo,
                telefone=form.cleaned_data.get('telefone', ''),
                departamento=form.cleaned_data.get('departamento', '')
            )
            
            # Registrar no AuditLog
            AuditLog.objects.create(
                usuario=request.user,
                acao='CRIAR_USUARIO',
                objeto=f'Usuario:{user.id}',
                dados={
                    'usuario': user.get_full_name(),
                    'email': user.email,
                    'tipo': tipo,
                    'username': username
                }
            )
            
            # Enviar email com senha temporária
            try:
                from .tasks import send_welcome_email_with_password
                send_welcome_email_with_password.delay(user.id, senha_temporaria)
                messages.success(
                    request, 
                    f'Usuário {user.get_full_name()} criado com sucesso! '
                    f'Um email com a senha temporária foi enviado para {user.email}.'
                )
            except Exception as e:
                messages.warning(
                    request,
                    f'Usuário criado, mas houve erro ao enviar email. '
                    f'Senha temporária: {senha_temporaria}'
                )
            
            return redirect('usuarios:usuarios_list')
    else:
        form = CriarUsuarioForm()
    
    return render(request, 'usuarios/criar_usuario.html', {'form': form})


@login_required
@admin_required
def editar_perfil_usuario(request, pk):
    """
    Altera o tipo/perfil de um usuário.
    """
    usuario = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        novo_tipo = request.POST.get('tipo')
        if novo_tipo in dict(Perfil.PERFIL_CHOICES):
            perfil = usuario.perfil
            tipo_anterior = perfil.tipo
            perfil.tipo = novo_tipo
            perfil.save()
            
            # Registrar no AuditLog
            AuditLog.objects.create(
                usuario=request.user,
                acao='ALTERAR_PERFIL',
                objeto=f'Usuario:{usuario.id}',
                dados={
                    'usuario': usuario.get_full_name(),
                    'de': tipo_anterior,
                    'para': novo_tipo
                }
            )
            
            messages.success(
                request, 
                f'Perfil de {usuario.get_full_name()} alterado para {novo_tipo}'
            )
            from django.http import HttpResponseRedirect
            from django.urls import reverse
            return HttpResponseRedirect(reverse('usuarios:usuarios_list'))
    
    return render(request, 'usuarios/editar_perfil.html', {
        'usuario': usuario,
        'tipo_choices': Perfil.PERFIL_CHOICES
    })


@login_required
@admin_required
def redefinir_senha_usuario(request, pk):
    """
    Redefine a senha de um usuário.
    Gera uma senha temporária e envia por email.
    """
    usuario = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        nova_senha = secrets.token_urlsafe(12)[:12]
        usuario.set_password(nova_senha)
        usuario.save()
        
        # Registrar no AuditLog
        AuditLog.objects.create(
            usuario=request.user,
            acao='REDEFINIR_SENHA',
            objeto=f'Usuario:{usuario.id}',
            dados={'usuario': usuario.get_full_name()}
        )
        
        # Enviar email com nova senha
        try:
            from .tasks import send_password_reset_email
            send_password_reset_email.delay(usuario.id, nova_senha)
            messages.success(
                request, 
                f'Senha redefinida! Um email com a nova senha foi enviado para {usuario.email}.'
            )
        except Exception as e:
            messages.warning(
                request,
                f'Senha redefinida, mas houve erro ao enviar email. '
                f'Nova senha temporária: {nova_senha}'
            )
        
        return redirect('usuarios:usuarios_list')
    
    return render(request, 'usuarios/redefinir_senha.html', {'usuario': usuario})


@login_required
@admin_required
def excluir_usuario(request, pk):
    """
    Exclui um usuário do sistema (com confirmação).
    """
    usuario = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        confirmacao = request.POST.get('confirmacao', '').strip()
        nome_completo = usuario.get_full_name().strip()
        
        if confirmacao == nome_completo:
            # Registrar no AuditLog antes de deletar
            AuditLog.objects.create(
                usuario=request.user,
                acao='EXCLUIR_USUARIO',
                objeto=f'Usuario:{usuario.id}',
                dados={'usuario': nome_completo}
            )
            
            usuario.delete()
            messages.success(request, f'Usuário {nome_completo} foi excluído permanentemente.')
            return redirect('usuarios:usuarios_list')
        else:
            messages.error(request, 'Confirmação incorreta. Tente novamente.')
    
    return render(request, 'usuarios/excluir_confirm.html', {'usuario': usuario})


@login_required
@admin_required
def detalhes_usuario(request, pk):
    """
    Exibe os detalhes de um usuário em modal.
    """
    usuario = get_object_or_404(User, pk=pk)
    perfil = usuario.perfil
    
    # Último agendamento (para "última atividade")
    ultimo_agendamento = Agendamento.objects.filter(usuario=usuario).order_by('-data').first()
    
    context = {
        'usuario': usuario,
        'perfil': perfil,
        'ultimo_agendamento': ultimo_agendamento,
        'total_agendamentos': Agendamento.objects.filter(usuario=usuario).count(),
    }
    
    return render(request, 'usuarios/detalhes_usuario.html', context)

