from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils.encoding import smart_str
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import csv

from agendamentos.models import Agendamento
from salas.models import Sala, Bloco
from administracao.models import Perfil


def coordenador_required(func):
    """Decorator para garantir que apenas coordenadores/admins acessem."""
    def wrapper(request, *args, **kwargs):
        try:
            perfil = request.user.perfil
            if perfil.tipo not in ['COO', 'ADM']:
                messages.error(request, 'Você não tem permissão para acessar relatórios.')
                return HttpResponseRedirect(reverse('dashboard:dashboard'))
        except Perfil.DoesNotExist:
            messages.error(request, 'Perfil não encontrado.')
            return HttpResponseRedirect(reverse('dashboard:dashboard'))
        return func(request, *args, **kwargs)
    return wrapper


@login_required
@coordenador_required
def index(request):
    """
    Dashboard de relatórios com filtros avançados.
    Acessível apenas para Coordenadores e Admins.
    """
    perfil = request.user.perfil
    
    # ========================================================================
    # FILTROS
    # ========================================================================
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    sala_id = request.GET.get('sala')
    status_filter = request.GET.get('status')
    usuario_id = request.GET.get('usuario')
    
    # ========================================================================
    # QUERYSET BASE
    # ========================================================================
    agendamentos_qs = Agendamento.objects.all().select_related('usuario', 'sala', 'sala__bloco')
    
    # Aplicar filtros
    if data_inicio:
        agendamentos_qs = agendamentos_qs.filter(data__gte=data_inicio)
    
    if data_fim:
        agendamentos_qs = agendamentos_qs.filter(data__lte=data_fim)
    
    if sala_id:
        agendamentos_qs = agendamentos_qs.filter(sala_id=sala_id)
    
    if status_filter:
        agendamentos_qs = agendamentos_qs.filter(status=status_filter)
    
    if usuario_id:
        agendamentos_qs = agendamentos_qs.filter(usuario_id=usuario_id)
    
    # ========================================================================
    # ESTATÍSTICAS
    # ========================================================================
    total_agendamentos = agendamentos_qs.count()
    total_aprovados = agendamentos_qs.filter(status='A').count()
    total_pendentes = agendamentos_qs.filter(status='P').count()
    total_reprovados = agendamentos_qs.filter(status='R').count()
    
    # Taxa de aprovação
    taxa_aprovacao = round((total_aprovados / total_agendamentos * 100), 1) if total_agendamentos > 0 else 0
    
    # ========================================================================
    # DADOS PARA GRÁFICOS
    # ========================================================================
    
    # Agendamentos por status
    agendamentos_por_status = {
        'labels': ['Pendentes', 'Aprovados', 'Reprovados'],
        'values': [total_pendentes, total_aprovados, total_reprovados],
        'colors': ['#f59e0b', '#10b981', '#ef4444']
    }
    
    # Top 5 salas mais utilizadas (apenas aprovados)
    salas_mais_utilizadas = Sala.objects.annotate(
        total=Count('agendamentos', filter=Q(agendamentos__status='A'))
    ).order_by('-total')[:5]
    
    salas_chart = {
        'labels': [sala.nome for sala in salas_mais_utilizadas],
        'values': [sala.total for sala in salas_mais_utilizadas]
    }
    
    # Top 5 usuários com mais agendamentos aprovados
    usuarios_mais_ativos = User.objects.annotate(
        total=Count('agendamentos', filter=Q(agendamentos__status='A'))
    ).order_by('-total')[:5]
    
    usuarios_chart = {
        'labels': [f"{u.first_name} {u.last_name}" if u.first_name else u.username for u in usuarios_mais_ativos],
        'values': [u.total for u in usuarios_mais_ativos]
    }
    
    # ========================================================================
    # DADOS PARA OS FILTROS
    # ========================================================================
    todas_salas = Sala.objects.all().order_by('nome')
    todos_blocos = Bloco.objects.all().order_by('nome')
    todos_usuarios = User.objects.filter(perfil__isnull=False).order_by('first_name', 'last_name')
    
    # Lista de agendamentos com paginação
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    
    agendamentos_list = agendamentos_qs.order_by('-data', '-criado_em')
    paginator = Paginator(agendamentos_list, 15)  # 15 por página
    
    page = request.GET.get('page', 1)
    try:
        agendamentos_recentes = paginator.page(page)
    except PageNotAnInteger:
        agendamentos_recentes = paginator.page(1)
    except EmptyPage:
        agendamentos_recentes = paginator.page(paginator.num_pages)
    
    context = {
        'perfil': perfil,
        # Estatísticas
        'total_agendamentos': total_agendamentos,
        'total_aprovados': total_aprovados,
        'total_pendentes': total_pendentes,
        'total_reprovados': total_reprovados,
        'taxa_aprovacao': taxa_aprovacao,
        # Gráficos
        'agendamentos_por_status': agendamentos_por_status,
        'salas_chart': salas_chart,
        'usuarios_chart': usuarios_chart,
        # Tabelas
        'agendamentos_recentes': agendamentos_recentes,
        'is_paginated': paginator.num_pages > 1,
        # Filtros
        'todas_salas': todas_salas,
        'todos_blocos': todos_blocos,
        'todos_usuarios': todos_usuarios,
        'status_choices': Agendamento.STATUS_CHOICES,
        # Valores atuais dos filtros
        'data_inicio_filter': data_inicio,
        'data_fim_filter': data_fim,
        'sala_id_filter': sala_id,
        'status_filter': status_filter,
        'usuario_id_filter': usuario_id,
    }
    
    return render(request, 'relatorios/index.html', context)


@login_required
@coordenador_required
def export_csv(request):
    """
    Exporta agendamentos para CSV com os mesmos filtros da tela.
    Apenas Coordenadores e Admins podem exportar.
    """
    # Aplicar os mesmos filtros da view index
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    sala_id = request.GET.get('sala')
    status_filter = request.GET.get('status')
    usuario_id = request.GET.get('usuario')
    
    qs = Agendamento.objects.all().select_related('usuario', 'sala', 'sala__bloco')
    
    if data_inicio:
        qs = qs.filter(data__gte=data_inicio)
    if data_fim:
        qs = qs.filter(data__lte=data_fim)
    if sala_id:
        qs = qs.filter(sala_id=sala_id)
    if status_filter:
        qs = qs.filter(status=status_filter)
    if usuario_id:
        qs = qs.filter(usuario_id=usuario_id)
    
    # Criar arquivo CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    response['Content-Disposition'] = f'attachment; filename="agendamentos_{timestamp}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'ID',
        'Data',
        'Horário Início',
        'Horário Fim',
        'Sala',
        'Bloco',
        'Usuário',
        'Email',
        'Motivo',
        'Status',
        'Justificativa Reprovação',
        'Criado Em',
        'Atualizado Em'
    ])
    
    for ag in qs.order_by('-data', '-criado_em'):
        usuario_nome = f"{ag.usuario.first_name} {ag.usuario.last_name}".strip() or ag.usuario.username
        status_display = ag.get_status_display()
        bloco_nome = ag.sala.bloco.nome if ag.sala.bloco else 'N/A'
        
        writer.writerow([
            ag.id,
            ag.data.strftime('%d/%m/%Y'),
            ag.horario_inicio.strftime('%H:%M'),
            ag.horario_fim.strftime('%H:%M'),
            ag.sala.nome,
            bloco_nome,
            usuario_nome,
            ag.usuario.email,
            smart_str(ag.motivo),
            status_display,
            smart_str(ag.justificativa_reprovacao or ''),
            ag.criado_em.strftime('%d/%m/%Y %H:%M'),
            ag.atualizado_em.strftime('%d/%m/%Y %H:%M'),
        ])
    
    return response


@login_required
@coordenador_required
def export_salas_csv(request):
    """
    Exporta relatório de salas com estatísticas de uso.
    Apenas Admins podem exportar.
    """
    try:
        perfil = request.user.perfil
        if perfil.tipo != 'ADM':
            messages.error(request, 'Apenas administradores podem exportar este relatório.')
            return HttpResponseRedirect(reverse('relatorios:index'))
    except Perfil.DoesNotExist:
        return HttpResponseRedirect(reverse('dashboard:dashboard'))
    
    # Buscar salas com contagem de agendamentos
    salas = Sala.objects.annotate(
        total_agendamentos=Count('agendamentos'),
        total_aprovados=Count('agendamentos', filter=Q(agendamentos__status='A')),
        total_pendentes=Count('agendamentos', filter=Q(agendamentos__status='P')),
        total_reprovados=Count('agendamentos', filter=Q(agendamentos__status='R'))
    ).select_related('bloco').prefetch_related('recursos').order_by('nome')
    
    # Criar arquivo CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    response['Content-Disposition'] = f'attachment; filename="salas_{timestamp}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'ID',
        'Nome',
        'Bloco',
        'Capacidade',
        'Recursos',
        'Total Agendamentos',
        'Aprovados',
        'Pendentes',
        'Reprovados'
    ])
    
    for sala in salas:
        bloco_nome = sala.bloco.nome if sala.bloco else 'N/A'
        recursos = ', '.join([r.nome for r in sala.recursos.all()])
        
        writer.writerow([
            sala.id,
            sala.nome,
            bloco_nome,
            sala.capacidade,
            recursos,
            sala.total_agendamentos,
            sala.total_aprovados,
            sala.total_pendentes,
            sala.total_reprovados
        ])
    
    return response


@login_required
@coordenador_required
def export_pdf(request):
    """
    Exporta relatório de agendamentos em PDF.
    Apenas Coordenadores e Admins podem exportar.
    """
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib.enums import TA_CENTER
    from io import BytesIO
    
    # Aplicar filtros
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    sala_id = request.GET.get('sala')
    status_filter = request.GET.get('status')
    usuario_id = request.GET.get('usuario')
    
    qs = Agendamento.objects.all().select_related('usuario', 'sala', 'sala__bloco')
    
    if data_inicio:
        qs = qs.filter(data__gte=data_inicio)
    if data_fim:
        qs = qs.filter(data__lte=data_fim)
    if sala_id:
        qs = qs.filter(sala_id=sala_id)
    if status_filter:
        qs = qs.filter(status=status_filter)
    if usuario_id:
        qs = qs.filter(usuario_id=usuario_id)
    
    # Criar PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), topMargin=1*cm, bottomMargin=1*cm)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=14,
        alignment=TA_CENTER
    )
    
    # Título
    title = Paragraph('Relatório de Agendamentos - AgendeAqui', title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.5*cm))
    
    # Informações do filtro
    info_text = f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    if data_inicio or data_fim:
        periodo = f"Período: {data_inicio or '...'} até {data_fim or '...'}"
        info_text += f" | {periodo}"
    
    info = Paragraph(info_text, styles['Normal'])
    elements.append(info)
    elements.append(Spacer(1, 0.5*cm))
    
    # Dados da tabela
    data = [['ID', 'Data', 'Horário', 'Sala', 'Usuário', 'Status']]
    
    for ag in qs.order_by('-data', '-criado_em')[:100]:  # Limitar a 100 registros
        usuario_nome = f"{ag.usuario.first_name} {ag.usuario.last_name}".strip() or ag.usuario.username
        status_display = ag.get_status_display()
        horario = f"{ag.horario_inicio.strftime('%H:%M')} - {ag.horario_fim.strftime('%H:%M')}"
        
        data.append([
            str(ag.id),
            ag.data.strftime('%d/%m/%Y'),
            horario,
            ag.sala.nome,
            usuario_nome,
            status_display
        ])
    
    # Criar tabela
    table = Table(data, colWidths=[2*cm, 2.5*cm, 3*cm, 4*cm, 5*cm, 3*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    
    elements.append(table)
    
    # Gerar PDF
    doc.build(elements)
    
    # Retornar resposta
    buffer.seek(0)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="relatorio_agendamentos_{timestamp}.pdf"'
    
    return response
