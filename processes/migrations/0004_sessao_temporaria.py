# Generated migration for SessaoTemporaria model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('brewery', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('processes', '0003_meta'),
    ]

    operations = [
        migrations.CreateModel(
            name='SessaoTemporaria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chave_sessao', models.CharField(max_length=100, unique=True, verbose_name='Chave da Sessão')),
                ('criada_em', models.DateTimeField(auto_now_add=True, verbose_name='Criada em')),
                ('ultima_atividade', models.DateTimeField(auto_now=True, verbose_name='Última Atividade')),
                ('dados_limpis', models.BooleanField(default=False, verbose_name='Dados Limpos')),
                ('cervejaria', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sessoes_temporarias', to='brewery.brewery', verbose_name='Cervejaria')),
                ('usuario', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='sessao_temporaria', to=settings.AUTH_USER_MODEL, verbose_name='Usuário')),
            ],
            options={
                'verbose_name': 'Sessão Temporária',
                'verbose_name_plural': 'Sessões Temporárias',
                'ordering': ['-ultima_atividade'],
            },
        ),
    ]
