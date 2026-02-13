#!/usr/bin/env python
"""
Script de Validação - Verifica se tudo foi instalado corretamente
"""

import os
import sys
from pathlib import Path

# Cores para terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_header():
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}✓ VALIDAÇÃO DO SISTEMA DE DADOS TEMPORÁRIOS{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(msg):
    print(f"{Colors.GREEN}✓{Colors.END} {msg}")

def print_error(msg):
    print(f"{Colors.RED}✗{Colors.END} {msg}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠{Colors.END} {msg}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ{Colors.END} {msg}")

def check_arquivo(caminho, nome):
    """Verificar se arquivo existe"""
    if os.path.exists(caminho):
        print_success(f"{nome}")
        return True
    else:
        print_error(f"{nome} - NÃO ENCONTRADO: {caminho}")
        return False

def check_import(modulo, nome):
    """Verificar se módulo pode ser importado"""
    try:
        __import__(modulo)
        print_success(f"Módulo: {nome}")
        return True
    except ImportError as e:
        print_error(f"Módulo: {nome} - ERRO: {e}")
        return False

def main():
    print_header()
    
    total_checks = 0
    passed_checks = 0
    
    # ============================================
    # 1. VERIFICAR ARQUIVOS CRIADOS
    # ============================================
    print(f"{Colors.BLUE}1. ARQUIVOS PRINCIPAIS{Colors.END}\n")
    
    arquivos = [
        ('brewtab_config/middleware.py', 'Middleware'),
        ('brewtab_config/context_processors.py', 'Context Processor'),
        ('processes/dados_temporarios.py', 'Serviço de Gestão'),
        ('processes/management/commands/limpar_dados_temporarios.py', 'Comando de Limpeza'),
        ('processes/migrations/0004_sessao_temporaria.py', 'Migração do BD'),
        ('templates/components/dados_temporarios_widget.html', 'Widget Template'),
    ]
    
    for arquivo, nome in arquivos:
        total_checks += 1
        if check_arquivo(arquivo, nome):
            passed_checks += 1
    
    # ============================================
    # 2. VERIFICAR MODIFICAÇÕES EM ARQUIVOS
    # ============================================
    print(f"\n{Colors.BLUE}2. MODIFICAÇÕES EM ARQUIVOS{Colors.END}\n")
    
    # Verificar settings.py
    total_checks += 1
    try:
        with open('brewtab_config/settings.py', 'r', encoding='utf-8') as f:
            conteudo = f.read()
            if 'DADOS_TEMPORARIOS' in conteudo:
                print_success('settings.py - DADOS_TEMPORARIOS adicionado')
                passed_checks += 1
            else:
                print_error('settings.py - DADOS_TEMPORARIOS não encontrado')
    except Exception as e:
        print_error(f'settings.py - Erro: {e}')
    
    # Verificar middleware em settings
    total_checks += 1
    try:
        with open('brewtab_config/settings.py', 'r', encoding='utf-8') as f:
            conteudo = f.read()
            if 'DadosTemporarioMiddleware' in conteudo:
                print_success('settings.py - Middleware registrado')
                passed_checks += 1
            else:
                print_error('settings.py - Middleware não registrado')
    except Exception as e:
        print_error(f'settings.py - Erro: {e}')
    
    # Verificar context processor
    total_checks += 1
    try:
        with open('brewtab_config/settings.py', 'r', encoding='utf-8') as f:
            conteudo = f.read()
            if 'dados_temporarios_context' in conteudo:
                print_success('settings.py - Context Processor registrado')
                passed_checks += 1
            else:
                print_error('settings.py - Context Processor não registrado')
    except Exception as e:
        print_error(f'settings.py - Erro: {e}')
    
    # Verificar modelo SessaoTemporaria
    total_checks += 1
    try:
        with open('processes/models.py', 'r', encoding='utf-8') as f:
            conteudo = f.read()
            if 'SessaoTemporaria' in conteudo:
                print_success('models.py - Modelo SessaoTemporaria adicionado')
                passed_checks += 1
            else:
                print_error('models.py - Modelo SessaoTemporaria não encontrado')
    except Exception as e:
        print_error(f'models.py - Erro: {e}')
    
    # Verificar admin
    total_checks += 1
    try:
        with open('processes/admin.py', 'r', encoding='utf-8') as f:
            conteudo = f.read()
            if 'SessaoTemporariaAdmin' in conteudo:
                print_success('admin.py - SessaoTemporariaAdmin registrado')
                passed_checks += 1
            else:
                print_error('admin.py - SessaoTemporariaAdmin não registrado')
    except Exception as e:
        print_error(f'admin.py - Erro: {e}')
    
    # ============================================
    # 3. VERIFICAR DOCUMENTAÇÃO
    # ============================================
    print(f"\n{Colors.BLUE}3. DOCUMENTAÇÃO{Colors.END}\n")
    
    docs = [
        ('DADOS_TEMPORARIOS.md', 'Guia Completo'),
        ('GUIA_IMPLANTACAO.md', 'Guia de Implantação'),
        ('DADOS_TEMPORARIOS_RESUMO.md', 'Resumo da Implementação'),
        ('EXEMPLOS_IMPLEMENTACAO.py', 'Exemplos de Código'),
        ('IMPLEMENTACAO_COMPLETA.md', 'Implementação Completa'),
    ]
    
    for doc, nome in docs:
        total_checks += 1
        if check_arquivo(doc, nome):
            passed_checks += 1
    
    # ============================================
    # 4. PRÓXIMOS PASSOS
    # ============================================
    print(f"\n{Colors.BLUE}4. PRÓXIMOS PASSOS{Colors.END}\n")
    
    print_info("Execute os seguintes comandos:\n")
    print(f"  1. {Colors.YELLOW}python manage.py migrate{Colors.END}")
    print(f"     → Cria a tabela SessaoTemporaria\n")
    
    print(f"  2. {Colors.YELLOW}python manage.py limpar_dados_temporarios{Colors.END}")
    print(f"     → Testa o comando (sem expiração ainda)\n")
    
    print(f"  3. {Colors.YELLOW}python manage.py runserver{Colors.END}")
    print(f"     → Inicia o servidor\n")
    
    print(f"  4. Visite: {Colors.YELLOW}http://localhost:8000/admin/processes/sessaotemporaria/{Colors.END}")
    print(f"     → Verifique se a tabela foi criada\n")
    
    # ============================================
    # 5. CONFIGURAÇÕES
    # ============================================
    print(f"\n{Colors.BLUE}5. CONFIGURAÇÕES RECOMENDADAS{Colors.END}\n")
    
    print_info("Adicione em settings.py ou .env:\n")
    print(f"""    {Colors.YELLOW}DADOS_TEMPORARIOS = True{Colors.END}
    {Colors.YELLOW}DADOS_TEMPORARIOS_TIMEOUT = 30{Colors.END}  # minutos
    {Colors.YELLOW}DADOS_TEMPORARIOS_MAX_DB_SIZE_MB = 50{Colors.END}  # MB
    """)
    
    # ============================================
    # 6. RESUMO
    # ============================================
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}RESUMO DA VALIDAÇÃO{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    percentual = (passed_checks / total_checks * 100) if total_checks > 0 else 0
    
    print(f"Total de verificações: {total_checks}")
    print(f"Verificações passadas: {passed_checks}")
    print(f"Percentual: {percentual:.1f}%\n")
    
    if passed_checks == total_checks:
        print_success("\n✓ TUDO FOI IMPLEMENTADO CORRETAMENTE!")
        print_success("✓ Sistema pronto para usar!\n")
        return 0
    else:
        print_warning(f"\n⚠ {total_checks - passed_checks} verificação(ões) falharam")
        print_warning("⚠ Verifique os erros acima\n")
        return 1

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Operação cancelada{Colors.END}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Erro: {e}{Colors.END}\n")
        sys.exit(1)
