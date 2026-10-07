from django.contrib.auth.models import Group, User
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


class MigracaoGruposDeAcessoTest(TransactionTestCase):
    """A migração 0008 cria os grupos e mantém o acesso de quem já era staff."""

    antes = [('core', '0007_turmaperseveranca_mej')]
    depois = [('core', '0008_acesso_grupos')]

    def setUp(self):
        executor = MigrationExecutor(connection)
        executor.migrate(self.antes)
        # O schema de auth não muda nesta migração: dá para usar os modelos reais.
        User.objects.create(username='coordenadora', is_staff=True, is_active=True)
        User.objects.create(username='staff_inativo', is_staff=True, is_active=False)
        User.objects.create(username='comum', is_staff=False, is_active=True)

        executor = MigrationExecutor(connection)
        executor.loader.build_graph()
        executor.migrate(self.depois)

    def tearDown(self):
        executor = MigrationExecutor(connection)
        executor.loader.build_graph()
        executor.migrate(executor.loader.graph.leaf_nodes())

    def grupos(self, username):
        return set(User.objects.get(username=username).groups.values_list('name', flat=True))

    def test_grupos_criados(self):
        self.assertEqual(set(Group.objects.values_list('name', flat=True)), {'secretaria', 'coordenacao'})

    def test_staff_ativo_vai_para_coordenacao(self):
        self.assertEqual(self.grupos('coordenadora'), {'coordenacao'})

    def test_staff_inativo_e_usuario_comum_ficam_sem_grupo(self):
        self.assertEqual(self.grupos('staff_inativo'), set())
        self.assertEqual(self.grupos('comum'), set())
