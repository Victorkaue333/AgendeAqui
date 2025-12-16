from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Notificacao


@login_required
def lista(request):
    notificacoes = Notificacao.objects.filter(usuario=request.user)[:200]
    nao_lidas = Notificacao.objects.filter(usuario=request.user, lida=False).count()

    context = {
        'notificacoes': notificacoes,
        'nao_lidas': nao_lidas,
    }
    return render(request, 'notificacoes/lista.html', context)


@login_required
def marcar_lida(request, notificacao_id: int):
    if request.method != 'POST':
        return redirect('notificacoes:lista')

    notificacao = get_object_or_404(Notificacao, id=notificacao_id, usuario=request.user)
    if not notificacao.lida:
        notificacao.lida = True
        notificacao.lida_em = timezone.now()
        notificacao.save(update_fields=['lida', 'lida_em'])

    # Sempre redirecionar de volta para lista de notificações
    return redirect('notificacoes:lista')


@login_required
def marcar_todas_lidas(request):
    if request.method != 'POST':
        return redirect('notificacoes:lista')

    qs = Notificacao.objects.filter(usuario=request.user, lida=False)
    updated = qs.update(lida=True, lida_em=timezone.now())

    if updated:
        messages.success(request, f'✅ {updated} notificação(ões) marcada(s) como lida(s).')

    return redirect('notificacoes:lista')
