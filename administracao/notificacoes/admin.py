from django.contrib import admin

from .models import Notificacao


@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'titulo', 'nivel', 'lida', 'criada_em')
    list_filter = ('nivel', 'lida', 'criada_em')
    search_fields = ('titulo', 'mensagem', 'usuario__username', 'usuario__email')
    ordering = ('-criada_em',)
