from django.urls import path
from . import views

app_name = 'agendamentos'

urlpatterns = [
    # Página principal de agendamentos (lista)
    path('', views.agendamentos, name='agendamentos'),
    
    # Visualização em calendário
    path('calendario/', views.calendario, name='calendario'),
    
    # API JSON para calendário
    path('api/eventos/', views.agendamentos_json, name='agendamentos_json'),
    
    # CRUD - Criar agendamento (Professor)
    path('solicitar/', views.AgendamentoCreateView.as_view(), name='create'),
    path('<int:pk>/', views.AgendamentoDetailView.as_view(), name='detail'),
    
    # Gestão - Coordenador
    path('pendentes/', views.AgendamentoPendentesListView.as_view(), name='pendentes'),
    path('<int:pk>/aprovar/', views.AgendamentoApproveView.as_view(), name='approve'),
    path('aprovados/', views.agendamentos_aprovados, name='aprovados'),
    
    # Perfil do usuário
    path('meus-agendamentos/', views.meus_agendamentos, name='meus_agendamentos'),
]