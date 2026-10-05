from datetime import date

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


class MigracaoIdadeParaDataTest(TransactionTestCase):
    """A migração 0003 converte as idades (inteiros) em datas de nascimento."""

    antes = [('core', '0002_seed_turmas')]
    depois = [('core', '0003_turma_idade_para_data')]

    def setUp(self):
        executor = MigrationExecutor(connection)
        executor.migrate(self.antes)
        apps_antigos = executor.loader.project_state(self.antes).apps
        Turma = apps_antigos.get_model('core', 'Turma')
        Turma.objects.create(nome='Turma 9 a 11', idade_minima=9, idade_maxima=11)
        Turma.objects.create(nome='Turma livre')

        executor = MigrationExecutor(connection)
        executor.loader.build_graph()
        executor.migrate(self.depois)
        self.apps = executor.loader.project_state(self.depois).apps

    def tearDown(self):
        # Volta o banco de teste para a última migração
        executor = MigrationExecutor(connection)
        executor.loader.build_graph()
        executor.migrate(executor.loader.graph.leaf_nodes())

    def test_idades_viram_datas(self):
        Turma = self.apps.get_model('core', 'Turma')
        ano = date.today().year
        turma = Turma.objects.get(nome='Turma 9 a 11')
        self.assertEqual(turma.idade_maxima, date(ano - 11, 1, 1))
        self.assertEqual(turma.idade_minima, date(ano - 9, 12, 31))

    def test_turma_sem_restricao_continua_vazia(self):
        Turma = self.apps.get_model('core', 'Turma')
        turma = Turma.objects.get(nome='Turma livre')
        self.assertIsNone(turma.idade_minima)
        self.assertIsNone(turma.idade_maxima)
