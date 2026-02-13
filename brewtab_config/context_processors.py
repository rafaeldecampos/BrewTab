"""
Context processors para dados temporários
"""
from django.conf import settings


def dados_temporarios_context(request):
    """Adiciona informações de dados temporários ao contexto de templates"""
    context = {
        'dados_temporarios_ativo': getattr(settings, 'DADOS_TEMPORARIOS', False),
    }
    
    if context['dados_temporarios_ativo'] and request.user.is_authenticated:
        from processes.dados_temporarios import GestorDadosTemporarios
        
        context['tempo_sessao_restante'] = GestorDadosTemporarios.obter_tempo_sessao_restante(request.user)
        context['sessao_expirando'] = GestorDadosTemporarios.sessao_vai_expirar_em_breve(request.user)
        context['tamanho_database'] = GestorDadosTemporarios.obter_tamanho_database()
        context['database_proxima_limite'] = GestorDadosTemporarios.database_proxima_limite()
    
    return context
