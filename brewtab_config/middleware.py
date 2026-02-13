"""
Middleware para gerenciamento de dados temporários em modo de hospedagem pública
"""
from django.conf import settings
from django.utils import timezone
from django.db import connection
import os


class DadosTemporarioMiddleware:
    """
    Middleware para gerenciar dados temporários quando DADOS_TEMPORARIOS está ativado.
    - Rastreia sessões de usuários
    - Limpa dados quando a sessão expira
    - Monitora tamanho do banco de dados
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.dados_temporarios_ativo = getattr(settings, 'DADOS_TEMPORARIOS', False)
    
    def __call__(self, request):
        if self.dados_temporarios_ativo:
            # Atualizar última atividade da sessão do usuário
            if request.user.is_authenticated:
                self._registrar_atividade_sessao(request)
                self._verificar_limpeza_necessaria()
        
        response = self.get_response(request)
        
        if self.dados_temporarios_ativo and request.user.is_authenticated:
            self._verificar_logout(request)
        
        return response
    
    def _registrar_atividade_sessao(self, request):
        """Registra a atividade da sessão atual do usuário"""
        from processes.models import SessaoTemporaria
        
        try:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key
            
            sessao, criada = SessaoTemporaria.objects.get_or_create(
                usuario=request.user,
                defaults={
                    'chave_sessao': session_key,
                }
            )
            
            # Atualizar chave de sessão se mudou
            if sessao.chave_sessao != session_key:
                sessao.chave_sessao = session_key
            
            # Atualizar última atividade
            sessao.ultima_atividade = timezone.now()
            
            # Se houver cervejaria na sessão, registrar
            if 'brewery_id' in request.session:
                from brewery.models import Brewery
                try:
                    sessao.cervejaria = Brewery.objects.get(id=request.session['brewery_id'])
                except Brewery.DoesNotExist:
                    pass
            
            sessao.save()
        except Exception as e:
            print(f"Erro ao registrar atividade de sessão: {e}")
    
    def _verificar_limpeza_necessaria(self):
        """Verifica se é necessário fazer limpeza de dados"""
        from processes.models import SessaoTemporaria
        from django.utils import timezone
        from datetime import timedelta
        
        timeout_minutos = getattr(settings, 'DADOS_TEMPORARIOS_TIMEOUT', 30)
        limite_tempo = timezone.now() - timedelta(minutes=timeout_minutos)
        
        # Encontrar sessões expiradas
        sessoes_expiradas = SessaoTemporaria.objects.filter(
            ultima_atividade__lt=limite_tempo,
            dados_limpis=False
        )
        
        for sessao in sessoes_expiradas:
            self._limpar_dados_usuario(sessao.usuario)
            sessao.dados_limpis = True
            sessao.save()
        
        # Verificar tamanho do banco de dados
        self._verificar_tamanho_database()
    
    def _limpar_dados_usuario(self, usuario):
        """Limpa todos os dados temporários de um usuário"""
        from brewery.models import Brewery
        from processes.models import (
            Processo, EtapaProcesso, ExecutacaoProcesso,
            ExecucaoEtapa, HistoricoExecucao, RegistroHaccp,
            PontoCriticoHaccp, Meta
        )
        
        try:
            # Limpar cervejarias do usuário
            cervejarias = Brewery.objects.filter(owner=usuario)
            
            for cervejaria in cervejarias:
                # Limpar processos, etapas e execuções
                Processo.objects.filter(cervejaria=cervejaria).delete()
                
                # Limpar pontos críticos e metas
                PontoCriticoHaccp.objects.filter(cervejaria=cervejaria).delete()
                RegistroHaccp.objects.filter(cervejaria=cervejaria).delete()
                Meta.objects.filter(cervejaria=cervejaria).delete()
            
            # Limpar cervejarias
            cervejarias.delete()
            
            print(f"Dados do usuário '{usuario.username}' foram limpos com sucesso.")
        
        except Exception as e:
            print(f"Erro ao limpar dados do usuário '{usuario.username}': {e}")
    
    def _verificar_tamanho_database(self):
        """Verifica se o banco de dados excedeu o tamanho máximo"""
        try:
            tamanho_max_mb = getattr(settings, 'DADOS_TEMPORARIOS_MAX_DB_SIZE_MB', 50)
            
            db_file = getattr(settings, 'DATABASES', {}).get('default', {}).get('NAME', '')
            
            if db_file and os.path.exists(db_file):
                tamanho_mb = os.path.getsize(db_file) / (1024 * 1024)
                
                if tamanho_mb > tamanho_max_mb:
                    print(f"Banco de dados excedeu tamanho máximo ({tamanho_mb:.2f}MB > {tamanho_max_mb}MB)")
                    self._limpar_todos_dados()
        
        except Exception as e:
            print(f"Erro ao verificar tamanho do banco de dados: {e}")
    
    def _limpar_todos_dados(self):
        """Limpa todos os dados de todos os usuários (exceto admin)"""
        from django.contrib.auth.models import User
        from processes.models import SessaoTemporaria
        
        try:
            # Limpar sessões
            SessaoTemporaria.objects.all().delete()
            
            # Limpar dados de todos os usuários (exceto superusuários)
            usuarios = User.objects.filter(is_superuser=False)
            for usuario in usuarios:
                self._limpar_dados_usuario(usuario)
            
            print("Limpeza completa do banco de dados foi realizada.")
        
        except Exception as e:
            print(f"Erro ao fazer limpeza completa: {e}")
    
    def _verificar_logout(self, request):
        """Verifica se houve logout e limpa dados da sessão"""
        if not request.session.session_key:
            from processes.models import SessaoTemporaria
            try:
                SessaoTemporaria.objects.filter(usuario=request.user).update(dados_limpis=True)
            except:
                pass
