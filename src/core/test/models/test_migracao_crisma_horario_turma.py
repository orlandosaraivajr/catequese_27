from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


class MigracaoHorarioCrismaParaTurmaTest(TransactionTestCase):
    """A migração 0005 converte CrismaModel.horario (escolha fixa) em FK para TurmaCrisma."""

    antes = [('core', '0004_renomeia_turma_para_turmacatequeseinfantil')]
    depois = [('core', '0005_turmacrisma')]

    def setUp(self):
        executor = MigrationExecutor(connection)
        executor.migrate(self.antes)
        apps_antigos = executor.loader.project_state(self.antes).apps
        CrismaModel = apps_antigos.get_model('core', 'CrismaModel')
        for codigo, nome in (('1', 'Ana Quinta'), ('2', 'Bruno Sabado'), ('3', 'Carla Sabado')):
            CrismaModel.objects.create(
                nome=nome, sexo='F', data_nascimento='2010-01-01',
                endereco='Rua X', cidade='Rio Claro', uf='SP', horario=codigo,
            )

        executor = MigrationExecutor(connection)
        executor.loader.build_graph()
        executor.migrate(self.depois)
        self.apps = executor.loader.project_state(self.depois).apps

    def tearDown(self):
        # Volta o banco de teste para a última migração
        executor = MigrationExecutor(connection)
        executor.loader.build_graph()
        executor.migrate(executor.loader.graph.leaf_nodes())

    def test_horarios_viram_turmas(self):
        TurmaCrisma = self.apps.get_model('core', 'TurmaCrisma')
        nomes = list(TurmaCrisma.objects.order_by('ordem').values_list('nome', flat=True))
        self.assertEqual(nomes, ['Quinta às 19:30h', 'Sábado às 09h', 'Sábado às 10:30h'])

    def test_fichas_apontam_para_turma_do_antigo_horario(self):
        CrismaModel = self.apps.get_model('core', 'CrismaModel')
        esperado = {
            'Ana Quinta': 'Quinta às 19:30h',
            'Bruno Sabado': 'Sábado às 09h',
            'Carla Sabado': 'Sábado às 10:30h',
        }
        for nome, turma in esperado.items():
            self.assertEqual(CrismaModel.objects.get(nome=nome).turma.nome, turma)
