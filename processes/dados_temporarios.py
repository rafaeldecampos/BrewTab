"""
Serviço para gerenciamento de dados temporários
"""
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from processes.models import SessaoTemporaria
import os


class GestorDadosTemporarios:
    """
    Gerenciador central de dados temporários para modo de hospedagem pública
    """
    
    @staticmethod
    def esta_ativo():
        """Verifica se o modo de dados temporários está ativo"""
        return getattr(settings, 'DADOS_TEMPORARIOS', False)
    
    @staticmethod
    def criar_sessao_temporaria(usuario, session_key, cervejaria=None):
        """Cria uma nova sessão temporária para um usuário"""
        if not GestorDadosTemporarios.esta_ativo():
            return None
        
        try:
            sessao, criada = SessaoTemporaria.objects.get_or_create(
                usuario=usuario,
                defaults={
                    'chave_sessao': session_key,
                    'cervejaria': cervejaria,
                }
            )
            return sessao
        except Exception as e:
            print(f"Erro ao criar sessão temporária: {e}")
            return None
    
    @staticmethod
    def atualizar_atividade(usuario):
        """Atualiza a última atividade de um usuário"""
        if not GestorDadosTemporarios.esta_ativo():
            return
        
        try:
            sessao = SessaoTemporaria.objects.get(usuario=usuario, dados_limpis=False)
            sessao.ultima_atividade = timezone.now()
            sessao.save(update_fields=['ultima_atividade'])
        except SessaoTemporaria.DoesNotExist:
            pass
        except Exception as e:
            print(f"Erro ao atualizar atividade: {e}")
    
    @staticmethod
    def obter_tempo_sessao_restante(usuario):
        """Retorna quantos minutos restam para limpeza da sessão"""
        if not GestorDadosTemporarios.esta_ativo():
            return None
        
        try:
            sessao = SessaoTemporaria.objects.get(usuario=usuario, dados_limpis=False)
            timeout_minutos = getattr(settings, 'DADOS_TEMPORARIOS_TIMEOUT', 30)
            tempo_decorrido = (timezone.now() - sessao.ultima_atividade).total_seconds() / 60
            tempo_restante = max(0, timeout_minutos - tempo_decorrido)
            return int(tempo_restante)
        except SessaoTemporaria.DoesNotExist:
            return 0
        except Exception as e:
            print(f"Erro ao calcular tempo de sessão: {e}")
            return None
    
    @staticmethod
    def sessao_vai_expirar_em_breve(usuario, minutos=5):
        """Verifica se a sessão vai expirar nos próximos N minutos"""
        if not GestorDadosTemporarios.esta_ativo():
            return False
        
        tempo_restante = GestorDadosTemporarios.obter_tempo_sessao_restante(usuario)
        if tempo_restante is None:
            return False
        return tempo_restante <= minutos
    
    @staticmethod
    def obter_tamanho_database():
        """Retorna o tamanho do banco de dados em MB"""
        try:
            db_file = getattr(settings, 'DATABASES', {}).get('default', {}).get('NAME', '')
            if db_file and os.path.exists(db_file):
                return os.path.getsize(db_file) / (1024 * 1024)
        except Exception as e:
            print(f"Erro ao obter tamanho do banco: {e}")
        
        return 0
    
    @staticmethod
    def database_proxima_limite():
        """Verifica se o banco de dados está próximo do limite"""
        if not GestorDadosTemporarios.esta_ativo():
            return False
        
        tamanho_max_mb = getattr(settings, 'DADOS_TEMPORARIOS_MAX_DB_SIZE_MB', 50)
        tamanho_atual = GestorDadosTemporarios.obter_tamanho_database()
        
        # Avisar quando usar 80% do espaço
        limite_aviso = tamanho_max_mb * 0.80
        return tamanho_atual >= limite_aviso
    
    @staticmethod
    def limpar_dados_usuario(usuario):
        """Limpa todos os dados de um usuário"""
        from brewery.models import Brewery
        from processes.models import (
            Processo, PontoCriticoHaccp, RegistroHaccp, Meta
        )
        
        try:
            cervejarias = Brewery.objects.filter(owner=usuario)
            
            for cervejaria in cervejarias:
                Processo.objects.filter(cervejaria=cervejaria).delete()
                PontoCriticoHaccp.objects.filter(cervejaria=cervejaria).delete()
                RegistroHaccp.objects.filter(cervejaria=cervejaria).delete()
                Meta.objects.filter(cervejaria=cervejaria).delete()
            
            cervejarias.delete()
            
            # Marcar sessão como limpa
            try:
                sessao = SessaoTemporaria.objects.get(usuario=usuario)
                sessao.dados_limpis = True
                sessao.save()
            except SessaoTemporaria.DoesNotExist:
                pass
            
            return True
        except Exception as e:
            print(f"Erro ao limpar dados do usuário: {e}")
            return False
    
    @staticmethod
    def obter_informacoes_sessao(usuario):
        """Retorna informações sobre a sessão do usuário"""
        if not GestorDadosTemporarios.esta_ativo():
            return None
        
        try:
            sessao = SessaoTemporaria.objects.get(usuario=usuario, dados_limpis=False)
            return {
                'usuario': usuario.username,
                'criada_em': sessao.criada_em,
                'ultima_atividade': sessao.ultima_atividade,
                'minutos_inativo': sessao.minutos_inativo,
                'tempo_restante': GestorDadosTemporarios.obter_tempo_sessao_restante(usuario),
                'cervejaria': sessao.cervejaria,
            }
        except SessaoTemporaria.DoesNotExist:
            return None
        except Exception as e:
            print(f"Erro ao obter informações da sessão: {e}")
            return None
    
    @staticmethod
    def obter_todas_sessoes_ativas():
        """Retorna todas as sessões ativas"""
        try:
            return SessaoTemporaria.objects.filter(dados_limpis=False).select_related('usuario')
        except Exception as e:
            print(f"Erro ao obter sessões ativas: {e}")
            return SessaoTemporaria.objects.none()
