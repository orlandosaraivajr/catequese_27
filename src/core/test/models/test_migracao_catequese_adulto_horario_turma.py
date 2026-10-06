from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


class MigracaoHorarioCatequeseAdultoParaTurmaTest(TransactionTestCase):
    """A migração 0006 converte CatequeseAdultoModel.horario em FK para TurmaCatequeseAdulto."""

    antes = [('core', '0005_turmacrisma')]
    depois = [('core', '0006_turmacatequeseadulto')]

    def setUp(self):
        executor = MigrationExecutor(connection)
        executor.migrate(self.antes)
        apps_antigos = executor.loader.project_state(self.antes).apps
        CatequeseAdultoModel = apps_antigos.get_model('core', 'CatequeseAdultoModel')
        # "1" era um horário já desativado (comentado no código); "4" e "5" ativos.
        for codigo, nome in (('4', 'Ana Quinta'), ('5', 'Bruno Sabado'), ('1', 'Carla Antiga')):
            CatequeseAdultoModel.objects.create(
                nome=nome, sexo='F', data_nascimento='1990-01-01', estado_civil='Solteira',
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

    def test_horarios_ativos_viram_turmas_ativas(self):
        TurmaCatequeseAdulto = self.apps.get_model('core', 'TurmaCatequeseAdulto')
        ativas = list(TurmaCatequeseAdulto.objects.filter(ativa=True).order_by('ordem').values_list('nome', flat=True))
        self.assertEqual(ativas, ['Quinta às 19:30h - SEM Batismo', 'Sábado às 09h - SEM Batismo'])

    def test_horario_desativado_em_uso_vira_turma_inativa(self):
        TurmaCatequeseAdulto = self.apps.get_model('core', 'TurmaCatequeseAdulto')
        turma = TurmaCatequeseAdulto.objects.get(nome='Terça às 19:30h - COM Batismo')
        self.assertFalse(turma.ativa)

    def test_horarios_desativados_sem_uso_nao_viram_turma(self):
        TurmaCatequeseAdulto = self.apps.get_model('core', 'TurmaCatequeseAdulto')
        self.assertFalse(TurmaCatequeseAdulto.objects.filter(
            nome__in=['Quarta às 19:30h - COM Batismo', 'Sábado às 08h - COM Batismo'],
        ).exists())

    def test_fichas_apontam_para_turma_do_antigo_horario(self):
        CatequeseAdultoModel = self.apps.get_model('core', 'CatequeseAdultoModel')
        esperado = {
            'Ana Quinta': 'Quinta às 19:30h - SEM Batismo',
            'Bruno Sabado': 'Sábado às 09h - SEM Batismo',
            'Carla Antiga': 'Terça às 19:30h - COM Batismo',
        }
        for nome, turma in esperado.items():
            self.assertEqual(CatequeseAdultoModel.objects.get(nome=nome).turma.nome, turma)
