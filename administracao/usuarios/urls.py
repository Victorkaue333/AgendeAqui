from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('cadastro/', views.cadastro, name='cadastro'),
    path('perfil/', views.perfil, name='perfil'),
    
    # Gerenciamento de Usuários (Admin Only)
    path('usuarios/', views.UsuariosListView.as_view(), name='usuarios_list'),
    path('usuarios/criar/', views.criar_usuario, name='criar_usuario'),
    path('usuarios/<int:pk>/editar-perfil/', views.editar_perfil_usuario, name='editar_perfil'),
    path('usuarios/<int:pk>/redefinir-senha/', views.redefinir_senha_usuario, name='redefinir_senha'),
    path('usuarios/<int:pk>/excluir/', views.excluir_usuario, name='excluir_usuario'),
    path('usuarios/<int:pk>/detalhes/', views.detalhes_usuario, name='detalhes_usuario'),
]
