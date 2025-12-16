from django.urls import path
from . import views

app_name = 'relatorios'

urlpatterns = [
    path('', views.index, name='index'),
    path('export/csv/', views.export_csv, name='export_csv'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),
    path('export/salas/csv/', views.export_salas_csv, name='export_salas_csv'),
]
