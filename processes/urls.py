from django.urls import path
from . import views

app_name = 'process'

urlpatterns = [
    # Processos
    path('cervejaria/<int:brewery_id>/', views.lista_processos, name='list'),
    path('cervejaria/<int:brewery_id>/criar/', views.criar_processo, name='create'),
    path('cervejaria/<int:brewery_id>/processo/<int:processo_id>/', views.detalhe_processo, name='detail'),
    path('cervejaria/<int:brewery_id>/processo/<int:processo_id>/editar/', views.editar_processo, name='edit'),
    path('cervejaria/<int:brewery_id>/processo/<int:processo_id>/deletar/', views.deletar_processo, name='delete'),
    
    # Etapas
    path('cervejaria/<int:brewery_id>/processo/<int:processo_id>/etapa/criar/', views.criar_etapa, name='create_step'),
    
    # ETAPA 3: Execução de Processos
    path('cervejaria/<int:brewery_id>/processo/<int:processo_id>/executar/', views.iniciar_execucao_processo, name='iniciar_execucao'),
    path('cervejaria/<int:brewery_id>/execucao/<int:execucao_id>/checklist/', views.checklist_execucao, name='checklist_execucao'),
    path('cervejaria/<int:brewery_id>/processo/<int:processo_id>/historico/', views.historico_execucoes, name='historico_execucoes'),
    
    # ETAPA 5: Pontos Críticos HACCP
    path('cervejaria/<int:brewery_id>/pontos-criticos/', views.listar_pontos_criticos_cervejaria, name='pontos_criticos_cervejaria'),
    path('cervejaria/<int:brewery_id>/processo/<int:processo_id>/pontos-criticos/', views.listar_pontos_criticos, name='ponto_critico_list'),
    path('cervejaria/<int:brewery_id>/processo/<int:processo_id>/etapa/<int:etapa_id>/ponto-critico/', views.criar_ponto_critico, name='criar_ponto_critico'),
    
    # ETAPA 6: Não Conformidades
    path('cervejaria/<int:brewery_id>/nao-conformidades/', views.listar_nao_conformidades, name='nao_conformidades'),
    path('cervejaria/<int:brewery_id>/nc/criar/', views.criar_nao_conformidade, name='criar_nc'),
    path('cervejaria/<int:brewery_id>/nc/<int:nc_id>/', views.detalhe_nao_conformidade, name='detalhe_nc'),
    
    # ETAPA 7: Ações Corretivas (CAPA)
    path('cervejaria/<int:brewery_id>/nc/<int:nc_id>/acao-corretiva/', views.criar_acao_corretiva, name='criar_capa'),
    
    # ETAPA 8: Dashboard e Relatórios
    path('cervejaria/<int:brewery_id>/dashboard/', views.dashboard_cervejaria, name='dashboard'),
    path('cervejaria/<int:brewery_id>/dre/', views.relatorio_dre, name='dre'),
]
