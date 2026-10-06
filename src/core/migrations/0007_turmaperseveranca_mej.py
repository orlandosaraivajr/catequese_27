import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models

# Antigas escolhas fixas de Perseveranca_MEJ_Model.HORARIO_PERSEVERANCA, agora viram turmas.
TURMAS = [
    dict(codigo="1", nome="Perseverança e MEJ - 11 a 14 anos - Quinta às 19:30h - Encontros na Capela NSGraças", ordem=1),
    dict(codigo="2", nome="MEJ - 15 a 25 anos - Quinta às 19:30h - Encontros na Capela NSGraças", ordem=2),
    dict(codigo="3", nome="Perseverança e MEJ - 11 a 14 anos - Terça às 19:30h - Encontros na Capela NSGraças", ordem=3),
    dict(codigo="4", nome="MEJ - 15 a 25 anos - Terça às 19:30h - Encontros na Capela NSGraças", ordem=4),
]


def horarios_para_turmas(apps, schema_editor):
    TurmaPerseveranca_MEJ = apps.get_model('core', 'TurmaPerseveranca_MEJ')
    Perseveranca_MEJ_Model = apps.get_model('core', 'Perseveranca_MEJ_Model')
    for dados in TURMAS:
        turma, _ = TurmaPerseveranca_MEJ.objects.get_or_create(
            nome=dados['nome'], defaults={'ordem': dados['ordem'], 'ativa': True},
        )
        Perseveranca_MEJ_Model.objects.filter(horario=dados['codigo']).update(turma=turma)


def turmas_para_horarios(apps, schema_editor):
    TurmaPerseveranca_MEJ = apps.get_model('core', 'TurmaPerseveranca_MEJ')
    Perseveranca_MEJ_Model = apps.get_model('core', 'Perseveranca_MEJ_Model')
    for dados in TURMAS:
        Perseveranca_MEJ_Model.objects.filter(turma__nome=dados['nome']).update(horario=dados['codigo'])
    TurmaPerseveranca_MEJ.objects.filter(nome__in=[t['nome'] for t in TURMAS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_turmacatequeseadulto'),
    ]

    operations = [
        migrations.CreateModel(
            name='TurmaPerseveranca_MEJ',
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
            model_name='perseveranca_mej_model',
            name='turma',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='inscritos', to='core.turmaperseveranca_mej'),
        ),
        # Na volta, horario precisa aceitar nulo até ser preenchido de novo.
        migrations.AlterField(
            model_name='perseveranca_mej_model',
            name='horario',
            field=models.CharField(choices=[(t['codigo'], t['nome']) for t in TURMAS], max_length=2, null=True),
        ),
        migrations.RunPython(horarios_para_turmas, turmas_para_horarios),
        migrations.RemoveField(
            model_name='perseveranca_mej_model',
            name='horario',
        ),
        migrations.AlterField(
            model_name='perseveranca_mej_model',
            name='turma',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='inscritos', to='core.turmaperseveranca_mej'),
        ),
    ]
