from django.urls import path
from . import views

app_name = 'salas'

urlpatterns = [
    path('', views.SalaListView.as_view(), name='list'),
    path('create/', views.SalaCreateView.as_view(), name='create'),
    path('<int:pk>/', views.SalaDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.SalaUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.SalaDeleteView.as_view(), name='delete'),
]
