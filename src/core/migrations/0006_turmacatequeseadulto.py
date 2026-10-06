import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models

# Antigas escolhas de CatequeseAdultoModel.HORARIO_CATEQUESE_ADULTO, agora viram turmas.
# Os horários que estavam comentados no código (inativos) só viram turma se
# alguma ficha antiga ainda os referencia -- e nesse caso nascem desativados.
TURMAS = [
    dict(codigo="1", nome="Terça às 19:30h - COM Batismo", ordem=1, ativa=False),
    dict(codigo="3", nome="Quarta às 19:30h - COM Batismo", ordem=2, ativa=False),
    dict(codigo="4", nome="Quinta às 19:30h - SEM Batismo", ordem=3, ativa=True),
    dict(codigo="2", nome="Sábado às 08h - COM Batismo", ordem=4, ativa=False),
    dict(codigo="5", nome="Sábado às 09h - SEM Batismo", ordem=5, ativa=True),
]


def horarios_para_turmas(apps, schema_editor):
    TurmaCatequeseAdulto = apps.get_model('core', 'TurmaCatequeseAdulto')
    CatequeseAdultoModel = apps.get_model('core', 'CatequeseAdultoModel')
    for dados in TURMAS:
        fichas = CatequeseAdultoModel.objects.filter(horario=dados['codigo'])
        if not dados['ativa'] and not fichas.exists():
            continue
        turma, _ = TurmaCatequeseAdulto.objects.get_or_create(
            nome=dados['nome'], defaults={'ordem': dados['ordem'], 'ativa': dados['ativa']},
        )
        fichas.update(turma=turma)


def turmas_para_horarios(apps, schema_editor):
    TurmaCatequeseAdulto = apps.get_model('core', 'TurmaCatequeseAdulto')
    CatequeseAdultoModel = apps.get_model('core', 'CatequeseAdultoModel')
    for dados in TURMAS:
        CatequeseAdultoModel.objects.filter(turma__nome=dados['nome']).update(horario=dados['codigo'])
    TurmaCatequeseAdulto.objects.filter(nome__in=[t['nome'] for t in TURMAS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_turmacrisma'),
    ]

    operations = [
        migrations.CreateModel(
            name='TurmaCatequeseAdulto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=150)),
                ('ativa', models.BooleanField(default=True)),
                ('vagas_maximas', models.PositiveIntegerField(blank=True, help_text='Deixe em branco para não limitar o número de inscritos.', null=True)),
                ('idade_minima', models.DateField(blank=True, help_text='Data de nascimento mais recente aceita (alunos mais novos). Deixe em branco para não restringir.', null=True)),
                ('idade_maxima', models.DateField(blank=True, help_text='Data de nascimento mais antiga aceita (alunos mais velhos). Deixe em branco para não restringir.', null=True)),
                ('ordem', models.PositiveIntegerField(default=0)),
                ('criado_em', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'ordering': ['ordem', 'nome'],
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='catequeseadultomodel',
            name='turma',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='inscritos', to='core.turmacatequeseadulto'),
        ),
        # Na volta, horario precisa aceitar nulo até ser preenchido de novo.
        migrations.AlterField(
            model_name='catequeseadultomodel',
            name='horario',
            field=models.CharField(choices=[('4', 'Quinta às 19:30h - SEM Batismo'), ('5', 'Sábado às 09h - SEM Batismo')], max_length=2, null=True),
        ),
        migrations.RunPython(horarios_para_turmas, turmas_para_horarios),
        migrations.RemoveField(
            model_name='catequeseadultomodel',
            name='horario',
        ),
        migrations.AlterField(
            model_name='catequeseadultomodel',
            name='turma',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='inscritos', to='core.turmacatequeseadulto'),
        ),
    ]
