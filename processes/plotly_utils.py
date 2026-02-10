"""Utilitários para geração de gráficos Plotly"""
import json
from datetime import datetime, timedelta
import plotly.graph_objects as go
from django.db.models import Count, Q
from django.utils import timezone


def gerar_grafico_metas_comparacao(cervejaria):
    """
    Gera gráfico Plotly comparando Valor Atual vs Meta para todas as metas.
    Retorna JSON para integração em template Django.
    """
    from .models import Meta
    
    metas = Meta.objects.filter(cervejaria=cervejaria, ativo=True)
    
    if not metas.exists():
        return json.dumps({})
    
    nomes = [meta.nome for meta in metas]
    valores_atuais = [float(meta.valor_atual) for meta in metas]
    valores_metas = [float(meta.valor_meta) for meta in metas]
    
    fig = go.Figure(data=[
        go.Bar(name='Valor Atual', x=nomes, y=valores_atuais, marker_color='#2ecc71'),
        go.Bar(name='Meta', x=nomes, y=valores_metas, marker_color='#3498db')
    ])
    
    fig.update_layout(
        title='Comparação: Valor Atual vs Meta',
        xaxis_title='Metas',
        yaxis_title='Valor',
        barmode='group',
        hovermode='x unified',
        template='plotly_white',
        height=400,
        margin=dict(l=50, r=50, t=60, b=50)
    )
    
    return json.dumps(fig.to_dict())


def gerar_grafico_metas_progresso(cervejaria):
    """
    Gera gráfico de barra horizontal mostrando % de progresso de cada meta.
    """
    from .models import Meta
    
    metas = Meta.objects.filter(cervejaria=cervejaria, ativo=True)
    
    if not metas.exists():
        return json.dumps({})
    
    nomes = [meta.nome for meta in metas]
    percentuais = [meta.percentual_conclusao() for meta in metas]
    cores = ['#2ecc71' if p >= 100 else '#f39c12' if p >= 50 else '#e74c3c' for p in percentuais]
    
    fig = go.Figure(data=[
        go.Bar(
            y=nomes,
            x=percentuais,
            orientation='h',
            marker=dict(color=cores),
            text=[f'{p:.1f}%' for p in percentuais],
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title='Progresso das Metas (%)',
        xaxis_title='Percentual de Conclusão (%)',
        xaxis=dict(range=[0, 120]),
        yaxis_title='Metas',
        hovermode='y unified',
        template='plotly_white',
        height=300 + (len(metas) * 40),
        margin=dict(l=200, r=50, t=60, b=50)
    )
    
    return json.dumps(fig.to_dict())


def gerar_grafico_nc_por_severidade(cervejaria):
    """
    Gera gráfico de pizza mostrando distribuição de NCs por severidade.
    """
    from .models import NaoConformidade
    
    severidades = {
        'crítica': 'Crítica',
        'alta': 'Alta',
        'media': 'Média',
        'baixa': 'Baixa'
    }
    
    dados = []
    cores_map = {
        'crítica': '#dc3545',
        'alta': '#ff6b6b',
        'media': '#ffc107',
        'baixa': '#28a745'
    }
    
    for key, label in severidades.items():
        count = NaoConformidade.objects.filter(
            cervejaria=cervejaria,
            severidade=key
        ).count()
        if count > 0:
            dados.append({
                'severity': label,
                'count': count,
                'color': cores_map[key]
            })
    
    if not dados:
        return json.dumps({})
    
    labels = [d['severity'] for d in dados]
    values = [d['count'] for d in dados]
    colors = [d['color'] for d in dados]
    
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, marker=dict(colors=colors))])
    
    fig.update_layout(
        title='Não Conformidades por Severidade',
        hovermode='closest',
        template='plotly_white',
        height=400,
        margin=dict(l=50, r=50, t=60, b=50)
    )
    
    return json.dumps(fig.to_dict())


def gerar_grafico_nc_tendencia(cervejaria):
    """
    Gera gráfico de linha mostrando tendência de NCs nos últimos 30 dias.
    """
    from .models import NaoConformidade
    
    hoje = timezone.now()
    historico = []
    
    for i in range(29, -1, -1):
        data = (hoje - timedelta(days=i)).date()
        count = NaoConformidade.objects.filter(
            cervejaria=cervejaria,
            data_criacao__date=data
        ).count()
        historico.append({'data': data, 'count': count})
    
    datas = [h['data'].strftime('%d/%m') for h in historico]
    counts = [h['count'] for h in historico]
    
    fig = go.Figure(data=[
        go.Scatter(
            x=datas,
            y=counts,
            mode='lines+markers',
            name='NCs por Dia',
            line=dict(color='#e74c3c', width=2),
            marker=dict(size=6)
        )
    ])
    
    fig.update_layout(
        title='Tendência de Não Conformidades (Últimos 30 dias)',
        xaxis_title='Data',
        yaxis_title='Quantidade de NCs',
        hovermode='x unified',
        template='plotly_white',
        height=350,
        margin=dict(l=50, r=50, t=60, b=50)
    )
    
    return json.dumps(fig.to_dict())


def gerar_grafico_haccp_conformidade(cervejaria):
    """
    Gera gráfico de gauge mostrando taxa de conformidade HACCP.
    """
    from .models import RegistroHACCP
    
    total = RegistroHACCP.objects.filter(
        execucao__processo__cervejaria=cervejaria
    ).count()
    
    if total == 0:
        return json.dumps({})
    
    conformes = RegistroHACCP.objects.filter(
        execucao__processo__cervejaria=cervejaria,
        conforme=True
    ).count()
    
    percentual = (conformes / total) * 100
    
    fig = go.Figure(data=[go.Indicator(
        mode='gauge+number+delta',
        value=percentual,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': 'Taxa de Conformidade HACCP (%)'},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': '#2ecc71'},
            'steps': [
                {'range': [0, 50], 'color': '#ffe8d6'},
                {'range': [50, 80], 'color': '#fff3cd'},
                {'range': [80, 100], 'color': '#d4edda'}
            ],
            'threshold': {
                'line': {'color': 'red', 'width': 4},
                'thickness': 0.75,
                'value': 80
            }
        }
    )])
    
    fig.update_layout(
        height=350,
        margin=dict(l=50, r=50, t=60, b=50),
        template='plotly_white'
    )
    
    return json.dumps(fig.to_dict())


def gerar_grafico_execucoes_status(cervejaria):
    """
    Gera gráfico mostrando status das execuções de processos.
    """
    from .models import ExecutacaoProcesso
    
    status_choices = {
        'nao_iniciada': 'Não Iniciada',
        'em_progresso': 'Em Progresso',
        'concluida': 'Concluída',
        'cancelada': 'Cancelada'
    }
    
    dados = []
    cores_status = {
        'nao_iniciada': '#95a5a6',
        'em_progresso': '#3498db',
        'concluida': '#2ecc71',
        'cancelada': '#e74c3c'
    }
    
    for status_key, status_label in status_choices.items():
        count = ExecutacaoProcesso.objects.filter(
            processo__cervejaria=cervejaria,
            status=status_key
        ).count()
        if count > 0:
            dados.append({
                'status': status_label,
                'count': count,
                'color': cores_status[status_key]
            })
    
    if not dados:
        return json.dumps({})
    
    labels = [d['status'] for d in dados]
    values = [d['count'] for d in dados]
    colors = [d['color'] for d in dados]
    
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, marker=dict(colors=colors))])
    
    fig.update_layout(
        title='Status das Execuções de Processos',
        hovermode='closest',
        template='plotly_white',
        height=400,
        margin=dict(l=50, r=50, t=60, b=50)
    )
    
    return json.dumps(fig.to_dict())


def gerar_grafico_dre_receita_custos(cervejaria, periodo_dias=30):
    """
    Gera gráfico para DRE mostrando Receita vs Custos (mock data).
    Em produção, conectar a dados reais de sistema financeiro.
    """
    from .models import KPIExercicio
    
    # Mock data - substituir com dados reais do sistema financeiro
    categorias = ['Receita Bruta', 'Custos de Produção', 'Custos Operacionais', 'Lucro Líquido']
    valores = [100000, 45000, 25000, 30000]
    cores = ['#2ecc71', '#e74c3c', '#f39c12', '#3498db']
    
    fig = go.Figure(data=[go.Bar(
        x=categorias,
        y=valores,
        marker=dict(color=cores),
        text=[f'R$ {v:,.0f}' for v in valores],
        textposition='auto',
    )])
    
    fig.update_layout(
        title=f'DRE - Últimos {periodo_dias} dias',
        yaxis_title='Valor (R$)',
        hovermode='x unified',
        template='plotly_white',
        height=400,
        margin=dict(l=50, r=50, t=60, b=50)
    )
    
    return json.dumps(fig.to_dict())


def gerar_grafico_dre_metas_vs_real(cervejaria):
    """
    Gera gráfico para DRE comparando Metas vs Valores Reais.
    """
    from .models import Meta
    
    metas = Meta.objects.filter(
        cervejaria=cervejaria,
        ativo=True,
        tipo__in=['lucro', 'orcamento']
    )
    
    if not metas.exists():
        return json.dumps({})
    
    nomes = [meta.nome for meta in metas]
    valores_reais = [float(meta.valor_atual) for meta in metas]
    valores_metas = [float(meta.valor_meta) for meta in metas]
    
    fig = go.Figure(data=[
        go.Bar(name='Valor Real (R$)', x=nomes, y=valores_reais, marker_color='#2ecc71'),
        go.Bar(name='Meta (R$)', x=nomes, y=valores_metas, marker_color='#3498db')
    ])
    
    fig.update_layout(
        title='DRE: Valores Reais vs Metas Orçamentárias',
        xaxis_title='Categorias',
        yaxis_title='Valor (R$)',
        barmode='group',
        hovermode='x unified',
        template='plotly_white',
        height=400,
        margin=dict(l=50, r=50, t=60, b=50)
    )
    
    return json.dumps(fig.to_dict())


def gerar_grafico_kpi_resumo(cervejaria):
    """
    Gera gráfico com KPIs principais em formato de cards (via Plotly Indicator).
    """
    from .models import ExecutacaoProcesso, NaoConformidade, RegistroHACCP
    
    total_exec = ExecutacaoProcesso.objects.filter(
        processo__cervejaria=cervejaria
    ).count()
    
    exec_concluidas = ExecutacaoProcesso.objects.filter(
        processo__cervejaria=cervejaria,
        status='concluida'
    ).count()
    
    ncs_ativas = NaoConformidade.objects.filter(
        cervejaria=cervejaria,
        status__in=['aberta', 'em_analise', 'em_correcao']
    ).count()
    
    registros_haccp = RegistroHACCP.objects.filter(
        execucao__processo__cervejaria=cervejaria
    ).count()
    
    conformes = RegistroHACCP.objects.filter(
        execucao__processo__cervejaria=cervejaria,
        conforme=True
    ).count()
    
    taxa_haccp = (conformes / registros_haccp * 100) if registros_haccp > 0 else 0
    
    fig = go.Figure()
    
    fig.add_trace(go.Indicator(
        mode='number',
        value=total_exec,
        title={'text': 'Total Execuções'},
        domain={'x': [0, 0.25], 'y': [0.6, 1]}
    ))
    
    fig.add_trace(go.Indicator(
        mode='number',
        value=exec_concluidas,
        title={'text': 'Execuções Concluídas'},
        domain={'x': [0.25, 0.5], 'y': [0.6, 1]}
    ))
    
    fig.add_trace(go.Indicator(
        mode='number',
        value=ncs_ativas,
        title={'text': 'NCs Ativas'},
        domain={'x': [0.5, 0.75], 'y': [0.6, 1]}
    ))
    
    fig.add_trace(go.Indicator(
        mode='number+gauge',
        value=taxa_haccp,
        title={'text': 'Taxa HACCP (%)'},
        gauge={'axis': {'range': [0, 100]}},
        domain={'x': [0.75, 1], 'y': [0.6, 1]}
    ))
    
    fig.update_layout(
        height=200,
        margin=dict(l=20, r=20, t=40, b=20),
        template='plotly_white'
    )
    
    return json.dumps(fig.to_dict())
