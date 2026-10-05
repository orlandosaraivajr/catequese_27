import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models

# Antigas escolhas fixas de CrismaModel.HORARIO_CRISMA, agora viram turmas.
TURMAS = [
    dict(codigo="1", nome="Quinta às 19:30h", ordem=1),
    dict(codigo="2", nome="Sábado às 09h", ordem=2),
    dict(codigo="3", nome="Sábado às 10:30h", ordem=3),
]


def horarios_para_turmas(apps, schema_editor):
    TurmaCrisma = apps.get_model('core', 'TurmaCrisma')
    CrismaModel = apps.get_model('core', 'CrismaModel')
    for dados in TURMAS:
        turma, _ = TurmaCrisma.objects.get_or_create(
            nome=dados['nome'], defaults={'ordem': dados['ordem'], 'ativa': True},
        )
        CrismaModel.objects.filter(horario=dados['codigo']).update(turma=turma)


def turmas_para_horarios(apps, schema_editor):
    TurmaCrisma = apps.get_model('core', 'TurmaCrisma')
    CrismaModel = apps.get_model('core', 'CrismaModel')
    for dados in TURMAS:
        CrismaModel.objects.filter(turma__nome=dados['nome']).update(horario=dados['codigo'])
    TurmaCrisma.objects.filter(nome__in=[t['nome'] for t in TURMAS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_renomeia_turma_para_turmacatequeseinfantil'),
    ]

    operations = [
        migrations.CreateModel(
            name='TurmaCrisma',
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
            model_name='crismamodel',
            name='turma',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='inscritos', to='core.turmacrisma'),
        ),
        # Na volta, horario precisa aceitar nulo até ser preenchido de novo.
        migrations.AlterField(
            model_name='crismamodel',
            name='horario',
            field=models.CharField(choices=[('1', 'Quinta às 19:30h'), ('2', 'Sábado às 09h'), ('3', 'Sábado às 10:30h')], max_length=2, null=True),
        ),
        migrations.RunPython(horarios_para_turmas, turmas_para_horarios),
        migrations.RemoveField(
            model_name='crismamodel',
            name='horario',
        ),
        migrations.AlterField(
            model_name='crismamodel',
            name='turma',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='inscritos', to='core.turmacrisma'),
        ),
    ]
