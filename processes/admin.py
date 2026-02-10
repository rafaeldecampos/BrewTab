from django.contrib import admin
from .models import (
    Processo, EtapaProcesso, ExecutacaoProcesso, ExecucaoEtapa, 
    HistoricoExecucao, PontoCriticoHACCP, RegistroHACCP, NaoConformidade, 
    AcaoCorretiva, KPIExercicio
)


class EtapaProcessoInline(admin.TabularInline):
    model = EtapaProcesso
    extra = 1
    fields = ('ordem', 'nome', 'descricao')


@admin.register(Processo)
class ProcessoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cervejaria', 'get_categoria', 'criado_em')
    list_filter = ('categoria', 'cervejaria', 'criado_em')
    search_fields = ('nome', 'cervejaria__name')
    readonly_fields = ('criado_em', 'atualizado_em')
    inlines = [EtapaProcessoInline]
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('cervejaria', 'nome', 'categoria')
        }),
        ('Descrição', {
            'fields': ('descricao',),
            'classes': ('collapse',)
        }),
        ('Datas', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )

    def get_categoria(self, obj):
        return obj.get_categoria_display()
    get_categoria.short_description = 'Categoria'


@admin.register(EtapaProcesso)
class EtapaProcessoAdmin(admin.ModelAdmin):
    list_display = ('processo', 'ordem', 'nome')
    list_filter = ('processo__cervejaria', 'processo', 'ordem')
    search_fields = ('nome', 'processo__nome')
    readonly_fields = ('criado_em', 'atualizado_em')
    ordering = ('processo', 'ordem')


# ===== ETAPA 3: EXECUÇÃO DE PROCESSOS =====

class ExecucaoEtapaInline(admin.TabularInline):
    model = ExecucaoEtapa
    extra = 0
    readonly_fields = ('etapa', 'concluida', 'data_conclusao')
    fields = ('etapa', 'concluida', 'data_conclusao', 'observacoes')


@admin.register(ExecutacaoProcesso)
class ExecutacaoProcessoAdmin(admin.ModelAdmin):
    list_display = ('processo', 'usuario', 'get_status', 'data_inicio', 'data_conclusao')
    list_filter = ('status', 'processo__cervejaria', 'data_inicio')
    search_fields = ('processo__nome', 'usuario__username')
    readonly_fields = ('data_inicio', 'data_conclusao')
    inlines = [ExecucaoEtapaInline]
    
    def get_status(self, obj):
        return obj.get_status_display()
    get_status.short_description = 'Status'


@admin.register(ExecucaoEtapa)
class ExecucaoEtapaAdmin(admin.ModelAdmin):
    list_display = ('execucao', 'etapa', 'concluida', 'data_conclusao')
    list_filter = ('concluida', 'execucao__processo__cervejaria')
    search_fields = ('etapa__nome', 'execucao__processo__nome')
    readonly_fields = ('data_conclusao',)


# ===== ETAPA 4: RASTREAMENTO =====

@admin.register(HistoricoExecucao)
class HistoricoExecucaoAdmin(admin.ModelAdmin):
    list_display = ('execucao', 'usuario', 'acao', 'data_hora')
    list_filter = ('data_hora', 'execucao__processo__cervejaria')
    search_fields = ('acao', 'usuario__username')
    readonly_fields = ('data_hora',)
    ordering = ('-data_hora',)


# ===== ETAPA 5: PONTOS CRÍTICOS HACCP =====

@admin.register(PontoCriticoHACCP)
class PontoCriticoHACCPAdmin(admin.ModelAdmin):
    list_display = ('nome', 'processo', 'etapa', 'tipo', 'limite_minimo', 'limite_maximo')
    list_filter = ('tipo', 'processo__cervejaria', 'processo')
    search_fields = ('nome', 'processo__nome')
    readonly_fields = ('criado_em',)
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('processo', 'etapa', 'tipo', 'nome')
        }),
        ('Limites e Unidades', {
            'fields': ('limite_minimo', 'limite_maximo', 'unidade')
        }),
        ('Ações', {
            'fields': ('acao_preventiva', 'acao_corretiva')
        }),
        ('Responsabilidade', {
            'fields': ('responsavel', 'criado_em')
        }),
    )


@admin.register(RegistroHACCP)
class RegistroHACCPAdmin(admin.ModelAdmin):
    list_display = ('ponto_critico', 'valor_medido', 'conforme', 'usuario', 'data_hora')
    list_filter = ('conforme', 'ponto_critico__processo__cervejaria', 'data_hora')
    search_fields = ('ponto_critico__nome', 'usuario__username')
    readonly_fields = ('data_hora',)
    ordering = ('-data_hora',)


# ===== ETAPA 6: NÃO CONFORMIDADES =====

@admin.register(NaoConformidade)
class NaoConformidadeAdmin(admin.ModelAdmin):
    list_display = ('id', 'titulo', 'severidade', 'status', 'usuario_criacao', 'data_criacao')
    list_filter = ('severidade', 'status', 'cervejaria', 'data_criacao')
    search_fields = ('titulo', 'descricao', 'usuario_criacao__username')
    readonly_fields = ('data_criacao', 'usuario_criacao')
    ordering = ('-data_criacao',)
    fieldsets = (
        ('Identificação', {
            'fields': ('id', 'cervejaria', 'execucao', 'titulo')
        }),
        ('Detalhes', {
            'fields': ('descricao', 'severidade', 'status')
        }),
        ('Rastreamento', {
            'fields': ('usuario_criacao', 'data_criacao', 'data_fechamento')
        }),
    )


# ===== ETAPA 7: AÇÕES CORRETIVAS =====

class AcaoCorretivaInline(admin.TabularInline):
    model = AcaoCorretiva
    extra = 1
    fields = ('tipo', 'descricao', 'responsavel', 'data_prevista', 'status')


@admin.register(AcaoCorretiva)
class AcaoCorretivaAdmin(admin.ModelAdmin):
    list_display = ('nc', 'tipo', 'responsavel', 'data_prevista', 'status')
    list_filter = ('tipo', 'status', 'data_prevista', 'nc__cervejaria')
    search_fields = ('nc__titulo', 'descricao', 'responsavel__username')
    ordering = ('data_prevista', 'status')
    fieldsets = (
        ('Associação', {
            'fields': ('nc',)
        }),
        ('Ação Corretiva', {
            'fields': ('tipo', 'descricao', 'resultado')
        }),
        ('Planejamento', {
            'fields': ('responsavel', 'data_prevista', 'data_conclusao')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Auditoria', {
            'fields': ('data_criacao',)
        }),
    )
    readonly_fields = ('data_criacao',)


# ===== DRE: KPI E RESULTADO =====

@admin.register(KPIExercicio)
class KPIExercicioAdmin(admin.ModelAdmin):
    list_display = ('cervejaria', 'data_inicio', 'data_fim', 'taxa_conformidade', 'lucro_liquido')
    list_filter = ('cervejaria', 'data_inicio', 'data_fim')
    search_fields = ('cervejaria__name',)
    readonly_fields = ('criado_em', 'atualizado_em')
    fieldsets = (
        ('Período', {
            'fields': ('cervejaria', 'data_inicio', 'data_fim')
        }),
        ('Execução de Processos', {
            'fields': ('total_processos_executados', 'processos_sem_nc', 'taxa_conformidade')
        }),
        ('HACCP', {
            'fields': ('registros_haccp_conformes', 'registros_haccp_nao_conformes')
        }),
        ('Não Conformidades', {
            'fields': ('total_ncs', 'ncs_fechadas', 'ncs_criticas')
        }),
        ('Ações Corretivas', {
            'fields': ('total_capasscii', 'capas_concluidas')
        }),
        ('Resultado Financeiro', {
            'fields': ('receita_bruta', 'custos_produção', 'custos_operacionais', 'lucro_bruto', 'lucro_liquido')
        }),
        ('Datas', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )
