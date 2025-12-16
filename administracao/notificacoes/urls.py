from django.urls import path

from . import views

app_name = 'notificacoes'

urlpatterns = [
    path('', views.lista, name='lista'),
    path('marcar/<int:notificacao_id>/', views.marcar_lida, name='marcar_lida'),
    path('marcar-todas/', views.marcar_todas_lidas, name='marcar_todas_lidas'),
]
