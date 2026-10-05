from datetime import date

from django.db import migrations, models


def idades_para_datas(apps, schema_editor):
    """Converte as idades projetadas (inteiros) em datas de nascimento.

    A regra antiga usava idade = ano corrente - ano de nascimento, então:
    idade mínima N -> nascidos até 31/12/(ano - N)
    idade máxima M -> nascidos a partir de 01/01/(ano - M)
    """
    Turma = apps.get_model('core', 'Turma')
    ano = date.today().year
    for turma in Turma.objects.all():
        if turma.idade_minima is not None:
            turma.idade_minima_data = date(ano - turma.idade_minima, 12, 31)
        if turma.idade_maxima is not None:
            turma.idade_maxima_data = date(ano - turma.idade_maxima, 1, 1)
        turma.save(update_fields=['idade_minima_data', 'idade_maxima_data'])


def datas_para_idades(apps, schema_editor):
    Turma = apps.get_model('core', 'Turma')
    ano = date.today().year
    for turma in Turma.objects.all():
        turma.idade_minima = max(ano - turma.idade_minima_data.year, 0) if turma.idade_minima_data else None
        turma.idade_maxima = max(ano - turma.idade_maxima_data.year, 0) if turma.idade_maxima_data else None
        turma.save(update_fields=['idade_minima', 'idade_maxima'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_seed_turmas'),
    ]

    operations = [
        migrations.AddField(
            model_name='turma',
            name='idade_minima_data',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='turma',
            name='idade_maxima_data',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.RunPython(idades_para_datas, datas_para_idades),
        migrations.RemoveField(model_name='turma', name='idade_minima'),
        migrations.RemoveField(model_name='turma', name='idade_maxima'),
        migrations.RenameField(model_name='turma', old_name='idade_minima_data', new_name='idade_minima'),
        migrations.RenameField(model_name='turma', old_name='idade_maxima_data', new_name='idade_maxima'),
        migrations.AlterField(
            model_name='turma',
            name='idade_minima',
            field=models.DateField(
                blank=True, null=True,
                help_text='Data de nascimento mais recente aceita (alunos mais novos). Deixe em branco para não restringir.',
            ),
        ),
        migrations.AlterField(
            model_name='turma',
            name='idade_maxima',
            field=models.DateField(
                blank=True, null=True,
                help_text='Data de nascimento mais antiga aceita (alunos mais velhos). Deixe em branco para não restringir.',
            ),
        ),
    ]
