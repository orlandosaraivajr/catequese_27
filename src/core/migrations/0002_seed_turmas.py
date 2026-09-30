from django.db import migrations

TURMAS = [
    dict(nome="Pré-Catequese - Terça às 19:30h", ativa=True, idade_minima=6, idade_maxima=8, ordem=1),
    dict(nome="1a Etapa - Quarta às 19:30h", ativa=True, idade_minima=9, idade_maxima=11, ordem=2),
    dict(nome="Transferência", ativa=True, idade_minima=None, idade_maxima=None, ordem=99),
]


def seed_turmas(apps, schema_editor):
    Turma = apps.get_model('core', 'Turma')
    for dados in TURMAS:
        Turma.objects.get_or_create(nome=dados['nome'], defaults=dados)


def remover_turmas(apps, schema_editor):
    Turma = apps.get_model('core', 'Turma')
    Turma.objects.filter(nome__in=[t['nome'] for t in TURMAS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_turmas, remover_turmas),
    ]
