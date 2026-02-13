"""
Comando de gerenciamento para limpeza de dados temporários
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from processes.models import SessaoTemporaria


class Command(BaseCommand):
    help = 'Limpa dados temporários baseado em timeout e tamanho do banco de dados'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Força limpeza completa de todos os dados',
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Limpa dados apenas de um usuário específico',
        )

    def handle(self, *args, **options):
        dados_temporarios_ativo = getattr(settings, 'DADOS_TEMPORARIOS', False)
        
        if not dados_temporarios_ativo:
            self.stdout.write(self.style.WARNING('DADOS_TEMPORARIOS não está ativado'))
            return
        
        if options['force']:
            self._limpar_todos_dados()
        elif options['user']:
            self._limpar_usuario_especifico(options['user'])
        else:
            self._limpar_sessoes_expiradas()
            self._verificar_tamanho_database()

    def _limpar_sessoes_expiradas(self):
        """Limpa sessões que expiraram"""
        timeout_minutos = getattr(settings, 'DADOS_TEMPORARIOS_TIMEOUT', 30)
        limite_tempo = timezone.now() - timedelta(minutes=timeout_minutos)
        
        sessoes_expiradas = SessaoTemporaria.objects.filter(
            ultima_atividade__lt=limite_tempo,
            dados_limpis=False
        )
        
        count = sessoes_expiradas.count()
        
        for sessao in sessoes_expiradas:
            self._limpar_dados_usuario(sessao.usuario)
            sessao.dados_limpis = True
            sessao.save()
        
        if count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'✓ {count} sessão(ões) expirada(s) foram limpas')
            )
        else:
            self.stdout.write('Nenhuma sessão expirada encontrada')

    def _verificar_tamanho_database(self):
        """Verifica e limpa se banco de dados excedeu tamanho máximo"""
        import os
        
        try:
            tamanho_max_mb = getattr(settings, 'DADOS_TEMPORARIOS_MAX_DB_SIZE_MB', 50)
            db_file = getattr(settings, 'DATABASES', {}).get('default', {}).get('NAME', '')
            
            if db_file and os.path.exists(db_file):
                tamanho_mb = os.path.getsize(db_file) / (1024 * 1024)
                
                self.stdout.write(f'Tamanho do banco de dados: {tamanho_mb:.2f}MB (máx: {tamanho_max_mb}MB)')
                
                if tamanho_mb > tamanho_max_mb:
                    self.stdout.write(
                        self.style.WARNING(f'⚠ Banco de dados excedeu tamanho máximo!')
                    )
                    self._limpar_todos_dados()
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao verificar tamanho: {e}'))

    def _limpar_dados_usuario(self, usuario):
        """Limpa todos os dados de um usuário específico"""
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
            
            self.stdout.write(
                self.style.SUCCESS(f"✓ Dados do usuário '{usuario.username}' foram limpos")
            )
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erro ao limpar usuário '{usuario.username}': {e}"))

    def _limpar_usuario_especifico(self, username):
        """Limpa dados de um usuário específico"""
        from django.contrib.auth.models import User
        
        try:
            usuario = User.objects.get(username=username)
            self._limpar_dados_usuario(usuario)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Usuário '{username}' não encontrado"))

    def _limpar_todos_dados(self):
        """Limpa todos os dados de todos os usuários"""
        from django.contrib.auth.models import User
        
        try:
            SessaoTemporaria.objects.all().delete()
            
            usuarios = User.objects.filter(is_superuser=False)
            for usuario in usuarios:
                self._limpar_dados_usuario(usuario)
            
            self.stdout.write(self.style.SUCCESS('✓ Limpeza completa realizada com sucesso'))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro durante limpeza completa: {e}'))
