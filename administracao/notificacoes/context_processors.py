def notificacoes_nav(request):
    """Adiciona contador de não lidas para o sino na navegação."""
    try:
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return {'notificacoes_nao_lidas': 0}

        from .models import Notificacao

        return {
            'notificacoes_nao_lidas': Notificacao.objects.filter(usuario=user, lida=False).count(),
        }
    except Exception:
        # Fail-safe: nunca quebrar renderização do template
        return {'notificacoes_nao_lidas': 0}
