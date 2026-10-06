from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase

QUINTA_11_14 = "Perseverança e MEJ - 11 a 14 anos - Quinta às 19:30h - Encontros na Capela NSGraças"
QUINTA_15_25 = "MEJ - 15 a 25 anos - Quinta às 19:30h - Encontros na Capela NSGraças"
TERCA_11_14 = "Perseverança e MEJ - 11 a 14 anos - Terça às 19:30h - Encontros na Capela NSGraças"
TERCA_15_25 = "MEJ - 15 a 25 anos - Terça às 19:30h - Encontros na Capela NSGraças"


class MigracaoHorarioPerseverancaParaTurmaTest(TransactionTestCase):
    """A migração 0007 converte Perseveranca_MEJ_Model.horario em FK para TurmaPerseveranca_MEJ."""

    antes = [('core', '0006_turmacatequeseadulto')]
    depois = [('core', '0007_turmaperseveranca_mej')]

    def setUp(self):
        executor = MigrationExecutor(connection)
        executor.migrate(self.antes)
        apps_antigos = executor.loader.project_state(self.antes).apps
        Perseveranca_MEJ_Model = apps_antigos.get_model('core', 'Perseveranca_MEJ_Model')
        for codigo, nome in (('1', 'Ana'), ('2', 'Bruno'), ('3', 'Carla'), ('4', 'Davi')):
            Perseveranca_MEJ_Model.objects.create(
                nome=nome, sexo='F', data_nascimento='2012-01-01',
                endereco='Rua X', cidade='Rio Claro', uf='SP', horario=codigo,
                nome_responsavel='Resp Teste', cpf_responsavel='1', endereco_responsavel='Rua X',
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

    def test_horarios_viram_turmas_ativas(self):
        TurmaPerseveranca_MEJ = self.apps.get_model('core', 'TurmaPerseveranca_MEJ')
        nomes = list(TurmaPerseveranca_MEJ.objects.filter(ativa=True).order_by('ordem').values_list('nome', flat=True))
        self.assertEqual(nomes, [QUINTA_11_14, QUINTA_15_25, TERCA_11_14, TERCA_15_25])

    def test_fichas_apontam_para_turma_do_antigo_horario(self):
        Perseveranca_MEJ_Model = self.apps.get_model('core', 'Perseveranca_MEJ_Model')
        esperado = {'Ana': QUINTA_11_14, 'Bruno': QUINTA_15_25, 'Carla': TERCA_11_14, 'Davi': TERCA_15_25}
        for nome, turma in esperado.items():
            self.assertEqual(Perseveranca_MEJ_Model.objects.get(nome=nome).turma.nome, turma)
