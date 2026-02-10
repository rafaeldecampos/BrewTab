from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.utils import timezone
from django.db import models
from datetime import datetime
import json
from brewery.models import Brewery
from .models import (
    Processo, EtapaProcesso, ExecutacaoProcesso, ExecucaoEtapa, 
    HistoricoExecucao, PontoCriticoHACCP, RegistroHACCP, NaoConformidade, 
    AcaoCorretiva, KPIExercicio
)


def verifica_propriedade_cervejaria(user, cervejaria):
    """Verifica se o usuário é proprietário da cervejaria."""
    if cervejaria.owner != user:
        return False
    return True


@login_required(login_url='login')
def lista_processos(request, brewery_id):
    """Lista todos os processos de uma cervejaria."""
    cervejaria = get_object_or_404(Brewery, id=brewery_id)
    
    if not verifica_propriedade_cervejaria(request.user, cervejaria):
        return HttpResponseForbidden('Você não tem permissão para acessar esta cervejaria.')
    
    processos = Processo.objects.filter(cervejaria=cervejaria)
    return render(request, 'processes/processo_list.html', {
        'cervejaria': cervejaria,
        'processos': processos
    })


@login_required(login_url='login')
def detalhe_processo(request, brewery_id, processo_id):
    """Exibe detalhes de um processo e suas etapas."""
    cervejaria = get_object_or_404(Brewery, id=brewery_id)
    
    if not verifica_propriedade_cervejaria(request.user, cervejaria):
        return HttpResponseForbidden('Você não tem permissão para acessar esta cervejaria.')
    
    processo = get_object_or_404(Processo, id=processo_id, cervejaria=cervejaria)
    etapas = processo.etapas.all()
    
    return render(request, 'processes/processo_detail.html', {
        'cervejaria': cervejaria,
        'processo': processo,
        'etapas': etapas
    })


@login_required(login_url='login')
def criar_processo(request, brewery_id):
    """Cria um novo processo."""
    cervejaria = get_object_or_404(Brewery, id=brewery_id)
    
    if not verifica_propriedade_cervejaria(request.user, cervejaria):
        return HttpResponseForbidden('Você não tem permissão para acessar esta cervejaria.')
    
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        categoria = request.POST.get('categoria', '').strip()
        descricao = request.POST.get('descricao', '').strip()
        
        if not nome:
            messages.error(request, 'Nome do processo é obrigatório.')
            return render(request, 'processes/processo_form.html', {
                'cervejaria': cervejaria,
                'categorias': Processo.CATEGORIAS
            })
        
        if not categoria:
            messages.error(request, 'Categoria é obrigatória.')
            return render(request, 'processes/processo_form.html', {
                'cervejaria': cervejaria,
                'categorias': Processo.CATEGORIAS
            })
        
        if Processo.objects.filter(cervejaria=cervejaria, nome=nome).exists():
            messages.error(request, f'Já existe um processo chamado "{nome}" nesta cervejaria.')
            return render(request, 'processes/processo_form.html', {
                'cervejaria': cervejaria,
                'categorias': Processo.CATEGORIAS
            })
        
        processo = Processo.objects.create(
            cervejaria=cervejaria,
            nome=nome,
            categoria=categoria,
            descricao=descricao
        )
        messages.success(request, f'Processo "{processo.nome}" criado com sucesso.')
        return redirect('process:detail', brewery_id=cervejaria.id, processo_id=processo.id)
    
    return render(request, 'processes/processo_form.html', {
        'cervejaria': cervejaria,
        'categorias': Processo.CATEGORIAS
    })


@login_required(login_url='login')
def editar_processo(request, brewery_id, processo_id):
    """Edita um processo existente."""
    cervejaria = get_object_or_404(Brewery, id=brewery_id)
    
    if not verifica_propriedade_cervejaria(request.user, cervejaria):
        return HttpResponseForbidden('Você não tem permissão para acessar esta cervejaria.')
    
    processo = get_object_or_404(Processo, id=processo_id, cervejaria=cervejaria)
    
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        categoria = request.POST.get('categoria', '').strip()
        descricao = request.POST.get('descricao', '').strip()
        
        if not nome:
            messages.error(request, 'Nome do processo é obrigatório.')
            return render(request, 'processes/processo_form.html', {
                'cervejaria': cervejaria,
                'processo': processo,
                'categorias': Processo.CATEGORIAS
            })
        
        if not categoria:
            messages.error(request, 'Categoria é obrigatória.')
            return render(request, 'processes/processo_form.html', {
                'cervejaria': cervejaria,
                'processo': processo,
                'categorias': Processo.CATEGORIAS
            })
        
        if Processo.objects.filter(cervejaria=cervejaria, nome=nome).exclude(id=processo.id).exists():
            messages.error(request, f'Já existe outro processo chamado "{nome}" nesta cervejaria.')
            return render(request, 'processes/processo_form.html', {
                'cervejaria': cervejaria,
                'processo': processo,
                'categorias': Processo.CATEGORIAS
            })
        
        processo.nome = nome
        processo.categoria = categoria
        processo.descricao = descricao
        processo.save()
        messages.success(request, f'Processo "{processo.nome}" atualizado com sucesso.')
        return redirect('process:detail', brewery_id=cervejaria.id, processo_id=processo.id)
    
    return render(request, 'processes/processo_form.html', {
        'cervejaria': cervejaria,
        'processo': processo,
        'categorias': Processo.CATEGORIAS
    })


@login_required(login_url='login')
def deletar_processo(request, brewery_id, processo_id):
    """Deleta um processo."""
    cervejaria = get_object_or_404(Brewery, id=brewery_id)
    
    if not verifica_propriedade_cervejaria(request.user, cervejaria):
        return HttpResponseForbidden('Você não tem permissão para acessar esta cervejaria.')
    
    processo = get_object_or_404(Processo, id=processo_id, cervejaria=cervejaria)
    
    if request.method == 'POST':
        nome_processo = processo.nome
        processo.delete()
        messages.success(request, f'Processo "{nome_processo}" deletado com sucesso.')
        return redirect('process:list', brewery_id=cervejaria.id)
    
    return render(request, 'processes/processo_confirm_delete.html', {
        'cervejaria': cervejaria,
        'processo': processo
    })


@login_required(login_url='login')
def criar_etapa(request, brewery_id, processo_id):
    """Cria uma nova etapa de processo."""
    cervejaria = get_object_or_404(Brewery, id=brewery_id)
    
    if not verifica_propriedade_cervejaria(request.user, cervejaria):
        return HttpResponseForbidden('Você não tem permissão para acessar esta cervejaria.')
    
    processo = get_object_or_404(Processo, id=processo_id, cervejaria=cervejaria)
    
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        ordem = request.POST.get('ordem', '').strip()
        descricao = request.POST.get('descricao', '').strip()
        
        if not nome:
            messages.error(request, 'Nome da etapa é obrigatório.')
            return render(request, 'processes/etapa_form.html', {
                'cervejaria': cervejaria,
                'processo': processo
            })
        
        if not ordem:
            messages.error(request, 'Ordem da etapa é obrigatória.')
            return render(request, 'processes/etapa_form.html', {
                'cervejaria': cervejaria,
                'processo': processo
            })
        
        try:
            ordem = int(ordem)
            if ordem < 1:
                raise ValueError
        except ValueError:
            messages.error(request, 'Ordem deve ser um número positivo.')
            return render(request, 'processes/etapa_form.html', {
                'cervejaria': cervejaria,
                'processo': processo
            })
        
        if EtapaProcesso.objects.filter(processo=processo, ordem=ordem).exists():
            messages.error(request, f'Já existe uma etapa com a ordem {ordem} neste processo.')
            return render(request, 'processes/etapa_form.html', {
                'cervejaria': cervejaria,
                'processo': processo
            })
        
        etapa = EtapaProcesso.objects.create(
            processo=processo,
            nome=nome,
            ordem=ordem,
            descricao=descricao
        )
        messages.success(request, f'Etapa "{etapa.nome}" criada com sucesso.')
        return redirect('process:detail', brewery_id=cervejaria.id, processo_id=processo.id)
    
    return render(request, 'processes/etapa_form.html', {
        'cervejaria': cervejaria,
        'processo': processo
    })


# ===== ETAPA 3: EXECUÇÃO DE PROCESSOS =====

@login_required(login_url='login')
def iniciar_execucao_processo(request, brewery_id, processo_id):
    """Inicia a execução de um processo."""
    cervejaria = get_object_or_404(Brewery, id=brewery_id)
    
    if not verifica_propriedade_cervejaria(request.user, cervejaria):
        return HttpResponseForbidden('Você não tem permissão para acessar esta cervejaria.')
    
    processo = get_object_or_404(Processo, id=processo_id, cervejaria=cervejaria)
    
    # Cria nova execução
    execucao = ExecutacaoProcesso.objects.create(
        processo=processo,
        usuario=request.user,
        status='em_progresso'
    )
    
    # Cria etapas de execução baseadas nas etapas do processo
    for etapa in processo.etapas.all():
        ExecucaoEtapa.objects.create(
            execucao=execucao,
            etapa=etapa
        )
    
    # Registra no histórico
    HistoricoExecucao.objects.create(
        execucao=execucao,
        usuario=request.user,
        acao='Execução Iniciada',
        descricao=f'Usuário {request.user.username} iniciou a execução do processo'
    )
    
    messages.success(request, f'Execução de "{processo.nome}" iniciada com sucesso.')
    return redirect('process:checklist_execucao', brewery_id=cervejaria.id, execucao_id=execucao.id)


@login_required(login_url='login')
def checklist_execucao(request, brewery_id, execucao_id):
    """Exibe checklist de execução do processo com etapas."""
    cervejaria = get_object_or_404(Brewery, id=brewery_id)
    
    if not verifica_propriedade_cervejaria(request.user, cervejaria):
        return HttpResponseForbidden('Você não tem permissão para acessar esta cervejaria.')
    
    execucao = get_object_or_404(ExecutacaoProcesso, id=execucao_id, processo__cervejaria=cervejaria)
    etapas_execucao = execucao.etapas_executadas.all()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'marcar_etapa':
            etapa_exec_id = request.POST.get('etapa_id')
            etapa_exec = get_object_or_404(ExecucaoEtapa, id=etapa_exec_id, execucao=execucao)
            
            etapa_exec.concluida = True
            etapa_exec.data_conclusao = timezone.now()
            etapa_exec.observacoes = request.POST.get('observacoes', '')
            etapa_exec.save()
            
            HistoricoExecucao.objects.create(
                execucao=execucao,
                usuario=request.user,
                acao='Etapa Concluída',
                descricao=f'Etapa "{etapa_exec.etapa.nome}" (ordem {etapa_exec.etapa.ordem}) foi marcada como concluída'
            )
            messages.success(request, f'Etapa "{etapa_exec.etapa.nome}" marcada como concluída.')
        
        elif action == 'finalizar_execucao':
            observacoes_gerais = request.POST.get('observacoes_gerais', '')
            execucao.status = 'concluida'
            execucao.data_conclusao = timezone.now()
            execucao.observacoes = observacoes_gerais
            execucao.save()
            
            HistoricoExecucao.objects.create(
                execucao=execucao,
                usuario=request.user,
                acao='Execução Finalizada',
                descricao='Execução do processo foi finalizada'
            )
            messages.success(request, 'Execução do processo finalizada com sucesso.')
            return redirect('process:historico_execucoes', brewery_id=cervejaria.id, processo_id=execucao.processo.id)
        
        return redirect('process:checklist_execucao', brewery_id=cervejaria.id, execucao_id=execucao.id)
    
    return render(request, 'processes/execucao_checklist.html', {
        'cervejaria': cervejaria,
        'execucao': execucao,
        'etapas_execucao': etapas_execucao
    })


@login_required(login_url='login')
def historico_execucoes(request, brewery_id, processo_id):
    """Exibe histórico de todas as execuções de um processo."""
    cervejaria = get_object_or_404(Brewery, id=brewery_id)
    
    if not verifica_propriedade_cervejaria(request.user, cervejaria):
        return HttpResponseForbidden('Você não tem permissão para acessar esta cervejaria.')
    
    processo = get_object_or_404(Processo, id=processo_id, cervejaria=cervejaria)
    execucoes = ExecutacaoProcesso.objects.filter(processo=processo)
    
    # Calcula métricas para cada execução
    execucoes_com_metricas = []
    for execucao in execucoes:
        total_etapas = execucao.etapas_executadas.count()
        etapas_concluidas = execucao.etapas_executadas.filter(concluida=True).count()
        execucoes_com_metricas.append({
            'execucao': execucao,
            'total_etapas': total_etapas,
            'etapas_concluidas': etapas_concluidas
        })
    
    return render(request, 'processes/execucao_historico.html', {
        'cervejaria': cervejaria,
        'processo': processo,
        'execucoes': execucoes_com_metricas
    })


# ===== ETAPA 5: PONTOS CRÍTICOS HACCP =====

@login_required(login_url='login')
def listar_pontos_criticos_cervejaria(request, brewery_id):
    """Lista todos os pontos críticos HACCP de uma cervejaria."""
    cervejaria = get_object_or_404(Brewery, id=brewery_id)
    
    if not verifica_propriedade_cervejaria(request.user, cervejaria):
        return HttpResponseForbidden('Você não tem permissão para acessar esta cervejaria.')
    
    # Obter todos os pontos críticos de todos os processos da cervejaria
    pontos_criticos = PontoCriticoHACCP.objects.filter(processo__cervejaria=cervejaria).select_related('processo', 'etapa')
    
    # Agrupar por processo
    processos = Processo.objects.filter(cervejaria=cervejaria)
    processos_com_pontos = {}
    for processo in processos:
        pontos = pontos_criticos.filter(processo=processo)
        if pontos.exists():
            processos_com_pontos[processo] = pontos
    
    return render(request, 'processes/pontos_criticos_cervejaria.html', {
        'cervejaria': cervejaria,
        'processos_com_pontos': processos_com_pontos,
        'total_pontos': pontos_criticos.count()
    })


@login_required(login_url='login')
def listar_pontos_criticos(request, brewery_id, processo_id):
    """Lista pontos críticos HACCP de um processo."""
    cervejaria = get_object_or_404(Brewery, id=brewery_id)
    
    if not verifica_propriedade_cervejaria(request.user, cervejaria):
        return HttpResponseForbidden('Você não tem permissão para acessar esta cervejaria.')
    
    processo = get_object_or_404(Processo, id=processo_id, cervejaria=cervejaria)
    pontos_criticos = PontoCriticoHACCP.objects.filter(processo=processo)
    
    return render(request, 'processes/ponto_critico_list.html', {
        'cervejaria': cervejaria,
        'processo': processo,
        'pontos_criticos': pontos_criticos
    })


@login_required(login_url='login')
def criar_ponto_critico(request, brewery_id, processo_id, etapa_id):
    """Cria um novo ponto crítico HACCP."""
    cervejaria = get_object_or_404(Brewery, id=brewery_id)
    
    if not verifica_propriedade_cervejaria(request.user, cervejaria):
        return HttpResponseForbidden('Você não tem permissão para acessar esta cervejaria.')
    
    processo = get_object_or_404(Processo, id=processo_id, cervejaria=cervejaria)
    etapa = get_object_or_404(EtapaProcesso, id=etapa_id, processo=processo)
    
    if request.method == 'POST':
        tipo = request.POST.get('tipo', '').strip()
        nome = request.POST.get('nome', '').strip()
        limite_minimo = request.POST.get('limite_minimo', '').strip()
        limite_maximo = request.POST.get('limite_maximo', '').strip()
        unidade = request.POST.get('unidade', '').strip()
        acao_preventiva = request.POST.get('acao_preventiva', '').strip()
        acao_corretiva = request.POST.get('acao_corretiva', '').strip()
        
        # Validações
        if not all([tipo, nome, limite_minimo, limite_maximo, unidade, acao_preventiva, acao_corretiva]):
            messages.error(request, 'Todos os campos são obrigatórios.')
            return render(request, 'processes/ponto_critico_form.html', {
                'cervejaria': cervejaria,
                'processo': processo,
                'etapa': etapa,
                'tipos': PontoCriticoHACCP._meta.get_field('tipo').choices
            })
        
        try:
            limite_minimo = float(limite_minimo)
            limite_maximo = float(limite_maximo)
        except ValueError:
            messages.error(request, 'Limites devem ser números válidos.')
            return render(request, 'processes/ponto_critico_form.html', {
                'cervejaria': cervejaria,
                'processo': processo,
                'etapa': etapa
            })
        
        if limite_minimo >= limite_maximo:
            messages.error(request, 'Limite mínimo deve ser menor que o limite máximo.')
            return render(request, 'processes/ponto_critico_form.html', {
                'cervejaria': cervejaria,
                'processo': processo,
                'etapa': etapa
            })
        
        ponto = PontoCriticoHACCP.objects.create(
            processo=processo,
            etapa=etapa,
            tipo=tipo,
            nome=nome,
            limite_minimo=limite_minimo,
            limite_maximo=limite_maximo,
            unidade=unidade,
            acao_preventiva=acao_preventiva,
            acao_corretiva=acao_corretiva,
            responsavel=request.user
        )
        
        messages.success(request, f'Ponto crítico "{ponto.nome}" criado com sucesso.')
        return redirect('process:ponto_critico_list', brewery_id=cervejaria.id, processo_id=processo.id)
    
    return render(request, 'processes/ponto_critico_form.html', {
        'cervejaria': cervejaria,
        'processo': processo,
        'etapa': etapa,
        'tipos': PontoCriticoHACCP._meta.get_field('tipo').choices
    })


# ===== ETAPA 6: NÃO CONFORMIDADES =====

@login_required(login_url='login')
def listar_nao_conformidades(request, brewery_id):
    """Lista todas as não conformidades da cervejaria."""
    cervejaria = get_object_or_404(Brewery, id=brewery_id)
    
    if not verifica_propriedade_cervejaria(request.user, cervejaria):
        return HttpResponseForbidden('Você não tem permissão para acessar esta cervejaria.')
    
    nao_conformidades = NaoConformidade.objects.filter(cervejaria=cervejaria)
    
    return render(request, 'processes/nc_list.html', {
        'cervejaria': cervejaria,
        'nao_conformidades': nao_conformidades
    })


@login_required(login_url='login')
def criar_nao_conformidade(request, brewery_id):
    """Cria uma nova não conformidade."""
    cervejaria = get_object_or_404(Brewery, id=brewery_id)
    
    if not verifica_propriedade_cervejaria(request.user, cervejaria):
        return HttpResponseForbidden('Você não tem permissão para acessar esta cervejaria.')
    
    if request.method == 'POST':
        titulo = request.POST.get('titulo', '').strip()
        descricao = request.POST.get('descricao', '').strip()
        severidade = request.POST.get('severidade', '').strip()
        
        if not all([titulo, descricao, severidade]):
            messages.error(request, 'Título, descrição e severidade são obrigatórios.')
            return render(request, 'processes/nc_form.html', {
                'cervejaria': cervejaria,
                'severidades': NaoConformidade._meta.get_field('severidade').choices
            })
        
        nc = NaoConformidade.objects.create(
            cervejaria=cervejaria,
            titulo=titulo,
            descricao=descricao,
            severidade=severidade,
            usuario_criacao=request.user
        )
        
        messages.success(request, f'Não conformidade criada: NC-{nc.id}')
        return redirect('process:detalhe_nc', brewery_id=cervejaria.id, nc_id=nc.id)
    
    return render(request, 'processes/nc_form.html', {
        'cervejaria': cervejaria,
        'severidades': NaoConformidade._meta.get_field('severidade').choices
    })


@login_required(login_url='login')
def detalhe_nao_conformidade(request, brewery_id, nc_id):
    """Exibe detalhes de uma não conformidade."""
    cervejaria = get_object_or_404(Brewery, id=brewery_id)
    
    if not verifica_propriedade_cervejaria(request.user, cervejaria):
        return HttpResponseForbidden('Você não tem permissão para acessar esta cervejaria.')
    
    nc = get_object_or_404(NaoConformidade, id=nc_id, cervejaria=cervejaria)
    acoes_corretivas = nc.acoes_corretivas.all()
    
    return render(request, 'processes/nc_detalhe.html', {
        'cervejaria': cervejaria,
        'nc': nc,
        'acoes_corretivas': acoes_corretivas
    })


# ===== ETAPA 7: AÇÕES CORRETIVAS (CAPA) =====

@login_required(login_url='login')
def criar_acao_corretiva(request, brewery_id, nc_id):
    """Cria uma ação corretiva para uma não conformidade."""
    cervejaria = get_object_or_404(Brewery, id=brewery_id)
    
    if not verifica_propriedade_cervejaria(request.user, cervejaria):
        return HttpResponseForbidden('Você não tem permissão para acessar esta cervejaria.')
    
    nc = get_object_or_404(NaoConformidade, id=nc_id, cervejaria=cervejaria)
    
    if request.method == 'POST':
        tipo = request.POST.get('tipo', '').strip()
        descricao = request.POST.get('descricao', '').strip()
        data_prevista = request.POST.get('data_prevista', '')
        
        if not all([tipo, descricao, data_prevista]):
            messages.error(request, 'Tipo, descrição e data prevista são obrigatórios.')
            return render(request, 'processes/capa_form.html', {
                'cervejaria': cervejaria,
                'nc': nc,
                'tipos': [('correcao', 'Correção'), ('prevencao', 'Prevenção')]
            })
        
        try:
            data_prevista = datetime.strptime(data_prevista, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Data deve estar em formato válido (YYYY-MM-DD).')
            return render(request, 'processes/capa_form.html', {
                'cervejaria': cervejaria,
                'nc': nc
            })
        
        capa = AcaoCorretiva.objects.create(
            nc=nc,
            tipo=tipo,
            descricao=descricao,
            responsavel=request.user,
            data_prevista=data_prevista
        )
        
        # Atualiza status da NC para em_correcao se não estiver fechada
        if nc.status != 'fechada':
            nc.status = 'em_correcao'
            nc.save()
        
        messages.success(request, 'Ação corretiva criada com sucesso.')
        return redirect('process:detalhe_nc', brewery_id=cervejaria.id, nc_id=nc.id)
    
    return render(request, 'processes/capa_form.html', {
        'cervejaria': cervejaria,
        'nc': nc,
        'tipos': [('correcao', 'Correção'), ('prevencao', 'Prevenção')]
    })


# ===== ETAPA 8: DASHBOARD E RELATÓRIOS =====

@login_required(login_url='login')
def dashboard_cervejaria(request, brewery_id):
    """Dashboard com KPIs, indicadores e análise de tendências da cervejaria."""
    from datetime import timedelta
    cervejaria = get_object_or_404(Brewery, id=brewery_id)
    
    if not verifica_propriedade_cervejaria(request.user, cervejaria):
        return HttpResponseForbidden('Você não tem permissão para acessar esta cervejaria.')
    
    # Métricas de Processos
    processos = Processo.objects.filter(cervejaria=cervejaria)
    total_processos = processos.count()
    total_execucoes = ExecutacaoProcesso.objects.filter(processo__cervejaria=cervejaria).count()
    execucoes_concluidas = ExecutacaoProcesso.objects.filter(
        processo__cervejaria=cervejaria,
        status='concluida'
    ).count()
    
    # Métrica de Conformidade (quanto % de execuções sem NC)
    processos_com_nc = NaoConformidade.objects.filter(
        cervejaria=cervejaria,
        status__in=['aberta', 'em_analise', 'em_correcao']
    ).count()
    
    # Métricas de HACCP
    total_registros_haccp = RegistroHACCP.objects.filter(
        execucao__processo__cervejaria=cervejaria
    ).count()
    registros_nao_conformes = RegistroHACCP.objects.filter(
        execucao__processo__cervejaria=cervejaria,
        conforme=False
    ).count()
    
    # Não Conformidades
    ncs_ativas = NaoConformidade.objects.filter(
        cervejaria=cervejaria,
        status__in=['aberta', 'em_analise', 'em_correcao']
    ).count()
    ncs_criticas_ativas = NaoConformidade.objects.filter(
        cervejaria=cervejaria,
        severidade='critica',
        status__in=['aberta', 'em_analise', 'em_correcao']
    ).count()
    
    # Ações Corretivas
    capas_pendentes = AcaoCorretiva.objects.filter(
        nc__cervejaria=cervejaria,
        status__in=['planejada', 'em_execucao']
    ).count()
    capas_concluidas = AcaoCorretiva.objects.filter(
        nc__cervejaria=cervejaria,
        status='concluida'
    ).count()
    
    # Últimas não conformidades
    ultimas_ncs = NaoConformidade.objects.filter(
        cervejaria=cervejaria
    ).order_by('-data_criacao')[:5]
    
    # ===== ANÁLISE DE TENDÊNCIAS =====
    hoje = timezone.now()
    
    # Períodos para análise
    periodo_7 = hoje - timedelta(days=7)
    periodo_14 = hoje - timedelta(days=14)
    periodo_30 = hoje - timedelta(days=30)
    
    # Tendência de NC: últimos 7, 14 e 30 dias
    ncs_7_dias = NaoConformidade.objects.filter(
        cervejaria=cervejaria,
        data_criacao__gte=periodo_7
    ).count()
    
    ncs_14_dias = NaoConformidade.objects.filter(
        cervejaria=cervejaria,
        data_criacao__gte=periodo_14,
        data_criacao__lt=periodo_7
    ).count()
    
    ncs_30_dias = NaoConformidade.objects.filter(
        cervejaria=cervejaria,
        data_criacao__gte=periodo_30,
        data_criacao__lt=periodo_14
    ).count()
    
    # Calcular tendência (crescente/decrescente)
    tendencia_nc = 'estável'
    if ncs_7_dias > ncs_14_dias:
        tendencia_nc = 'crescente'
    elif ncs_7_dias < ncs_14_dias:
        tendencia_nc = 'decrescente'
    
    # NC por severidade
    ncs_critica = NaoConformidade.objects.filter(
        cervejaria=cervejaria, severidade='critica'
    ).count()
    ncs_alta = NaoConformidade.objects.filter(
        cervejaria=cervejaria, severidade='alta'
    ).count()
    ncs_media = NaoConformidade.objects.filter(
        cervejaria=cervejaria, severidade='media'
    ).count()
    ncs_baixa = NaoConformidade.objects.filter(
        cervejaria=cervejaria, severidade='baixa'
    ).count()
    
    # Tendência HACCP: desvios nos últimos 7, 14 e 30 dias
    desvios_7_dias = RegistroHACCP.objects.filter(
        execucao__processo__cervejaria=cervejaria,
        data_hora__gte=periodo_7,
        conforme=False
    ).count()
    
    desvios_14_dias = RegistroHACCP.objects.filter(
        execucao__processo__cervejaria=cervejaria,
        data_hora__gte=periodo_14,
        data_hora__lt=periodo_7,
        conforme=False
    ).count()
    
    desvios_30_dias = RegistroHACCP.objects.filter(
        execucao__processo__cervejaria=cervejaria,
        data_hora__gte=periodo_30,
        data_hora__lt=periodo_14,
        conforme=False
    ).count()
    
    # Calcular tendência HACCP
    tendencia_haccp = 'estável'
    if desvios_7_dias > desvios_14_dias:
        tendencia_haccp = 'piorando'
    elif desvios_7_dias < desvios_14_dias:
        tendencia_haccp = 'melhorando'
    
    # Taxa de conformidade HACCP
    taxa_conformidade_haccp = 0
    if total_registros_haccp > 0:
        taxa_conformidade_haccp = ((total_registros_haccp - registros_nao_conformes) / total_registros_haccp) * 100
    
    # Taxa de conformidade geral (execuções sem NC)
    taxa_conformidade_geral = 0
    if total_execucoes > 0:
        taxa_conformidade_geral = ((total_execucoes - processos_com_nc) / total_execucoes) * 100
    
    # NCs em aberto há mais tempo (não resolvidas)
    ncs_antigas = NaoConformidade.objects.filter(
        cervejaria=cervejaria,
        status__in=['aberta', 'em_analise', 'em_correcao']
    ).order_by('data_criacao')[:3]
    
    return render(request, 'processes/dashboard.html', {
        'cervejaria': cervejaria,
        'total_processos': total_processos,
        'total_execucoes': total_execucoes,
        'execucoes_concluidas': execucoes_concluidas,
        'processos_com_nc': processos_com_nc,
        'total_registros_haccp': total_registros_haccp,
        'registros_nao_conformes': registros_nao_conformes,
        'ncs_ativas': ncs_ativas,
        'ncs_criticas_ativas': ncs_criticas_ativas,
        'capas_pendentes': capas_pendentes,
        'capas_concluidas': capas_concluidas,
        'ultimas_ncs': ultimas_ncs,
        # Tendências
        'ncs_7_dias': ncs_7_dias,
        'ncs_14_dias': ncs_14_dias,
        'ncs_30_dias': ncs_30_dias,
        'tendencia_nc': tendencia_nc,
        'ncs_critica': ncs_critica,
        'ncs_alta': ncs_alta,
        'ncs_media': ncs_media,
        'ncs_baixa': ncs_baixa,
        'desvios_7_dias': desvios_7_dias,
        'desvios_14_dias': desvios_14_dias,
        'desvios_30_dias': desvios_30_dias,
        'tendencia_haccp': tendencia_haccp,
        'taxa_conformidade_haccp': taxa_conformidade_haccp,
        'taxa_conformidade_geral': taxa_conformidade_geral,
        'ncs_antigas': ncs_antigas,
    })


@login_required(login_url='login')
def relatorio_dre(request, brewery_id):
    """Demonstração de Resultado do Exercício (DRE)."""
    cervejaria = get_object_or_404(Brewery, id=brewery_id)
    
    if not verifica_propriedade_cervejaria(request.user, cervejaria):
        return HttpResponseForbidden('Você não tem permissão para acessar esta cervejaria.')
    
    # Buscar ou criar KPI do exercício
    from datetime import date, timedelta
    
    # Definir período: últimos 30, 90, 180 ou 365 dias
    periodo = request.GET.get('periodo', '30')
    hoje = date.today()
    
    if periodo == '30':
        data_inicio = hoje - timedelta(days=30)
    elif periodo == '90':
        data_inicio = hoje - timedelta(days=90)
    elif periodo == '180':
        data_inicio = hoje - timedelta(days=180)
    else:  # 365
        data_inicio = hoje - timedelta(days=365)
    
    # Calcular métricas para o período
    execucoes_periodo = ExecutacaoProcesso.objects.filter(
        processo__cervejaria=cervejaria,
        data_inicio__date__gte=data_inicio
    )
    
    total_processos_executados = execucoes_periodo.count()
    processos_sem_nc = execucoes_periodo.exclude(
        nc_geradas__isnull=False
    ).count()
    
    taxa_conformidade = 0
    if total_processos_executados > 0:
        taxa_conformidade = (processos_sem_nc / total_processos_executados) * 100
    
    # HACCP
    registros_haccp = RegistroHACCP.objects.filter(
        execucao__processo__cervejaria=cervejaria,
        data_hora__date__gte=data_inicio
    )
    registros_haccp_conformes = registros_haccp.filter(conforme=True).count()
    registros_haccp_nao_conformes = registros_haccp.filter(conforme=False).count()
    
    # NCs
    ncs_total = NaoConformidade.objects.filter(
        cervejaria=cervejaria,
        data_criacao__date__gte=data_inicio
    )
    ncs_abertas = ncs_total.filter(status='aberta').count()
    ncs_fechadas = ncs_total.filter(status='fechada').count()
    ncs_criticas = ncs_total.filter(severidade='critica').count()
    
    # CAPAs
    capas = AcaoCorretiva.objects.filter(
        nc__cervejaria=cervejaria,
        data_criacao__date__gte=data_inicio
    )
    capas_concluidas = capas.filter(status='concluida').count()
    
    return render(request, 'processes/relatorio_dre.html', {
        'cervejaria': cervejaria,
        'periodo': periodo,
        'data_inicio': data_inicio,
        'data_fim': hoje,
        'total_processos_executados': total_processos_executados,
        'processos_sem_nc': processos_sem_nc,
        'taxa_conformidade': round(taxa_conformidade, 2),
        'registros_haccp_conformes': registros_haccp_conformes,
        'registros_haccp_nao_conformes': registros_haccp_nao_conformes,
        'total_ncs': ncs_total.count(),
        'ncs_abertas': ncs_abertas,
        'ncs_fechadas': ncs_fechadas,
        'ncs_criticas': ncs_criticas,
        'total_capas': capas.count(),
        'capas_concluidas': capas_concluidas
    })
