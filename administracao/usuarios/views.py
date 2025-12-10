from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from agendamentos.models import Agendamento
from .forms import UserRegistrationForm


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
        # Atualizar dados pessoais
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
