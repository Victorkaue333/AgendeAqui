from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from .view import acesso_rapido, landinpage, login_view, cadastro
from usuarios.forms import CustomAuthenticationForm

urlpatterns = [
    path('', landinpage, name='landinpage'),
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='login.html', authentication_form=CustomAuthenticationForm, next_page='acesso_rapido'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('acesso_rapido/', acesso_rapido, name='acesso_rapido'),
    path('cadastro/', cadastro, name='cadastro'),
    path('salas/', include('salas.urls')),
    path('relatorios/', include('relatorios.urls')),
    path('agendamentos/', include('agendamentos.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('', include('usuarios.urls')),
]
