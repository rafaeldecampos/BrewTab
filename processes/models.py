from django.db import models
from django.contrib.auth.models import User
from brewery.models import Brewery


class Processo(models.Model):
    CATEGORIAS = [
        ('producao', 'Produção'),
        ('limpeza', 'Limpeza'),
        ('envase', 'Envase'),
        ('qualidade', 'Qualidade'),
    ]

    cervejaria = models.ForeignKey(Brewery, on_delete=models.CASCADE, related_name='processos', verbose_name='Cervejaria')
    nome = models.CharField(max_length=255, verbose_name='Nome do Processo')
    categoria = models.CharField(max_length=50, choices=CATEGORIAS, verbose_name='Categoria')
    descricao = models.TextField(blank=True, verbose_name='Descrição')
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Processo'
        verbose_name_plural = 'Processos'
        ordering = ['-criado_em']
        unique_together = ('cervejaria', 'nome')

    def __str__(self):
        return f"{self.nome} ({self.get_categoria_display()})"


class EtapaProcesso(models.Model):
    processo = models.ForeignKey(Processo, on_delete=models.CASCADE, related_name='etapas', verbose_name='Processo')
    nome = models.CharField(max_length=255, verbose_name='Nome da Etapa')
    ordem = models.PositiveIntegerField(verbose_name='Ordem')
    descricao = models.TextField(blank=True, verbose_name='Descrição')
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Etapa do Processo'
        verbose_name_plural = 'Etapas do Processo'
        ordering = ['ordem']
        unique_together = ('processo', 'ordem')

    def __str__(self):
        return f"[{self.processo.nome}] Etapa {self.ordem}: {self.nome}"


# ===== ETAPA 3: EXECUÇÃO DE PROCESSOS =====

class ExecutacaoProcesso(models.Model):
    """Rastreamento de execução de um processo em tempo real"""
    STATUS_CHOICES = [
        ('nao_iniciada', 'Não Iniciada'),
        ('em_progresso', 'Em Progresso'),
        ('concluida', 'Concluída'),
        ('cancelada', 'Cancelada'),
    ]

    processo = models.ForeignKey(Processo, on_delete=models.CASCADE, related_name='execucoes', verbose_name='Processo')
    usuario = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Usuário que Iniciou')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='nao_iniciada', verbose_name='Status')
    data_inicio = models.DateTimeField(auto_now_add=True, verbose_name='Data de Início')
    data_conclusao = models.DateTimeField(null=True, blank=True, verbose_name='Data de Conclusão')
    observacoes = models.TextField(blank=True, verbose_name='Observações Gerais')
    
    class Meta:
        verbose_name = 'Execução de Processo'
        verbose_name_plural = 'Execuções de Processo'
        ordering = ['-data_inicio']
    
    def __str__(self):
        return f"{self.processo.nome} - {self.get_status_display()} ({self.data_inicio.strftime('%d/%m/%Y %H:%M')})"


class ExecucaoEtapa(models.Model):
    """Rastreamento de execução de uma etapa específica dentro de uma execução de processo"""
    execucao = models.ForeignKey(ExecutacaoProcesso, on_delete=models.CASCADE, related_name='etapas_executadas', verbose_name='Execução do Processo')
    etapa = models.ForeignKey(EtapaProcesso, on_delete=models.CASCADE, verbose_name='Etapa')
    concluida = models.BooleanField(default=False, verbose_name='Concluída')
    data_conclusao = models.DateTimeField(null=True, blank=True, verbose_name='Data de Conclusão')
    observacoes = models.TextField(blank=True, verbose_name='Observações da Etapa')
    
    class Meta:
        verbose_name = 'Execução de Etapa'
        verbose_name_plural = 'Execuções de Etapasscii'
        ordering = ['etapa__ordem']
        unique_together = ('execucao', 'etapa')
    
    def __str__(self):
        return f"{self.execucao} - Etapa {self.etapa.ordem}: {self.etapa.nome}"


# ===== ETAPA 4: RASTREAMENTO DE EXECUÇÃO =====

class HistoricoExecucao(models.Model):
    """Log detalhado de todas as mudanças em uma execução"""
    execucao = models.ForeignKey(ExecutacaoProcesso, on_delete=models.CASCADE, related_name='historicos', verbose_name='Execução')
    usuario = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Usuário')
    acao = models.CharField(max_length=255, verbose_name='Ação Realizada')
    descricao = models.TextField(blank=True, verbose_name='Descrição da Mudança')
    data_hora = models.DateTimeField(auto_now_add=True, verbose_name='Data/Hora')
    
    class Meta:
        verbose_name = 'Histórico de Execução'
        verbose_name_plural = 'Históricos de Execução'
        ordering = ['-data_hora']
    
    def __str__(self):
        return f"{self.execucao} - {self.acao} ({self.data_hora.strftime('%d/%m/%Y %H:%M')})"


# ===== ETAPA 5: PONTOS CRÍTICOS HACCP =====

class PontoCriticoHACCP(models.Model):
    """Definição de Pontos Críticos de Controle conforme HACCP"""
    TIPO_CHOICES = [
        ('temperatura', 'Temperatura'),
        ('ph', 'pH'),
        ('tempo', 'Tempo'),
        ('pressao', 'Pressão'),
        ('concentracao', 'Concentração'),
        ('outro', 'Outro'),
    ]

    processo = models.ForeignKey(Processo, on_delete=models.CASCADE, related_name='pontos_criticos', verbose_name='Processo')
    etapa = models.ForeignKey(EtapaProcesso, on_delete=models.CASCADE, related_name='pontos_criticos', verbose_name='Etapa')
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES, verbose_name='Tipo de Ponto Crítico')
    nome = models.CharField(max_length=255, verbose_name='Nome do Ponto Crítico')
    limite_minimo = models.FloatField(verbose_name='Limite Mínimo')
    limite_maximo = models.FloatField(verbose_name='Limite Máximo')
    unidade = models.CharField(max_length=20, verbose_name='Unidade (°C, pH, min, etc)')
    acao_preventiva = models.TextField(verbose_name='Ação Preventiva')
    acao_corretiva = models.TextField(verbose_name='Ação Corretiva')
    responsavel = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Responsável')
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    
    class Meta:
        verbose_name = 'Ponto Crítico HACCP'
        verbose_name_plural = 'Pontos Críticos HACCP'
        ordering = ['etapa__ordem']
    
    def __str__(self):
        return f"[{self.processo.nome}] {self.nome}: {self.limite_minimo}-{self.limite_maximo} {self.unidade}"


class RegistroHACCP(models.Model):
    """Registro de um ponto crítico monitorado durante execução"""
    execucao = models.ForeignKey(ExecutacaoProcesso, on_delete=models.CASCADE, related_name='registros_haccp', verbose_name='Execução')
    ponto_critico = models.ForeignKey(PontoCriticoHACCP, on_delete=models.CASCADE, related_name='registros', verbose_name='Ponto Crítico')
    valor_medido = models.FloatField(verbose_name='Valor Medido')
    conforme = models.BooleanField(verbose_name='Conforme Limite?')
    usuario = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Usuário que Registrou')
    data_hora = models.DateTimeField(auto_now_add=True, verbose_name='Data/Hora do Registro')
    observacoes = models.TextField(blank=True, verbose_name='Observações')
    
    class Meta:
        verbose_name = 'Registro HACCP'
        verbose_name_plural = 'Registros HACCP'
        ordering = ['-data_hora']
    
    def __str__(self):
        status = '✓' if self.conforme else '✗'
        return f"{status} {self.ponto_critico.nome}: {self.valor_medido} {self.ponto_critico.unidade}"


# ===== ETAPA 6: NÃO CONFORMIDADES =====

class NaoConformidade(models.Model):
    """Registro de desvios ou não conformidades encontradas"""
    SEVERIDADE_CHOICES = [
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta'),
        ('critica', 'Crítica'),
    ]
    
    STATUS_CHOICES = [
        ('aberta', 'Aberta'),
        ('em_analise', 'Em Análise'),
        ('em_correcao', 'Em Correção'),
        ('fechada', 'Fechada'),
    ]

    cervejaria = models.ForeignKey(Brewery, on_delete=models.CASCADE, related_name='nao_conformidades', verbose_name='Cervejaria')
    execucao = models.ForeignKey(ExecutacaoProcesso, null=True, blank=True, on_delete=models.SET_NULL, related_name='nc_geradas', verbose_name='Execução Associada')
    titulo = models.CharField(max_length=255, verbose_name='Título da NC')
    descricao = models.TextField(verbose_name='Descrição da Não Conformidade')
    severidade = models.CharField(max_length=20, choices=SEVERIDADE_CHOICES, default='media', verbose_name='Severidade')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aberta', verbose_name='Status')
    usuario_criacao = models.ForeignKey(User, on_delete=models.PROTECT, related_name='ncs_criadas', verbose_name='Usuário que Criou')
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')
    data_fechamento = models.DateTimeField(null=True, blank=True, verbose_name='Data de Fechamento')
    
    class Meta:
        verbose_name = 'Não Conformidade'
        verbose_name_plural = 'Não Conformidades'
        ordering = ['-data_criacao', '-severidade']
    
    def __str__(self):
        return f"NC-{self.id}: {self.titulo} ({self.get_severidade_display()})"


# ===== ETAPA 7: AÇÕES CORRETIVAS (CAPA) =====

class AcaoCorretiva(models.Model):
    """Ações de Correção e Prevenção (CAPA) para não conformidades"""
    STATUS_CHOICES = [
        ('planejada', 'Planejada'),
        ('em_execucao', 'Em Execução'),
        ('concluida', 'Concluída'),
        ('cancelada', 'Cancelada'),
    ]

    nc = models.ForeignKey(NaoConformidade, on_delete=models.CASCADE, related_name='acoes_corretivas', verbose_name='Não Conformidade')
    tipo = models.CharField(max_length=50, choices=[('correcao', 'Correção'), ('prevencao', 'Prevenção')], verbose_name='Tipo de Ação')
    descricao = models.TextField(verbose_name='Descrição da Ação')
    responsavel = models.ForeignKey(User, on_delete=models.PROTECT, related_name='acoes_corretivas_responsavel', verbose_name='Responsável')
    data_prevista = models.DateField(verbose_name='Data Prevista de Conclusão')
    data_conclusao = models.DateField(null=True, blank=True, verbose_name='Data Real de Conclusão')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planejada', verbose_name='Status')
    resultado = models.TextField(blank=True, verbose_name='Resultado da Implementação')
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')
    
    class Meta:
        verbose_name = 'Ação Corretiva (CAPA)'
        verbose_name_plural = 'Ações Corretivas (CAPA)'
        ordering = ['data_prevista']
    
    def __str__(self):
        return f"{self.get_tipo_display()} para NC-{self.nc.id}: {self.nc.titulo}"


# ===== DRE: DEMONSTRAÇÃO DE RESULTADO DO EXERCÍCIO =====

class KPIExercicio(models.Model):
    """Indicadores de Desempenho e Resultado da Cervejaria"""
    cervejaria = models.OneToOneField(Brewery, on_delete=models.CASCADE, related_name='kpi', verbose_name='Cervejaria')
    data_inicio = models.DateField(verbose_name='Início do Período')
    data_fim = models.DateField(verbose_name='Fim do Período')
    
    # Métricas de Execução
    total_processos_executados = models.IntegerField(default=0, verbose_name='Total de Processos Executados')
    processos_sem_nc = models.IntegerField(default=0, verbose_name='Processos sem Não Conformidade')
    taxa_conformidade = models.FloatField(default=0, verbose_name='Taxa de Conformidade (%)')
    
    # Métricas de Qualidade / HACCP
    registros_haccp_conformes = models.IntegerField(default=0, verbose_name='Registros HACCP Conformes')
    registros_haccp_nao_conformes = models.IntegerField(default=0, verbose_name='Registros HACCP Não Conformes')
    
    # Não Conformidades
    total_ncs = models.IntegerField(default=0, verbose_name='Total de NCs Abertas')
    ncs_fechadas = models.IntegerField(default=0, verbose_name='NCs Fechadas')
    ncs_criticas = models.IntegerField(default=0, verbose_name='NCs Críticas Ativas')
    
    # Ações Corretivas
    total_capasscii = models.IntegerField(default=0, verbose_name='Total de CAPAs')
    capas_concluidas = models.IntegerField(default=0, verbose_name='CAPAs Concluídas')
    
    # Resultado Financeiro (preparado para futuro módulo de custos)
    receita_bruta = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Receita Bruta')
    custos_produção = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Custos de Produção')
    custos_operacionais = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Custos Operacionais')
    lucro_bruto = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Lucro Bruto')
    lucro_liquido = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Lucro Líquido')
    
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    class Meta:
        verbose_name = 'KPI do Exercício'
        verbose_name_plural = 'KPIs dos Exercícios'
    
    def __str__(self):
        return f"KPI {self.cervejaria.name} ({self.data_inicio.strftime('%d/%m/%Y')} a {self.data_fim.strftime('%d/%m/%Y')})"

