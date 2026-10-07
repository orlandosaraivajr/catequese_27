from datetime import date
from http import HTTPStatus

from django.contrib.auth.models import Group
from django.shortcuts import resolve_url as r
from django.test import TestCase

from core.models import CatequeseInfantilModel, TurmaCatequeseInfantil
from core.test.acessos import GRUPO_COORDENACAO, GRUPO_SECRETARIA, criar_usuario, logar

PASTORAIS = ('', '_crisma', '_perseveranca_mej', '_adulto', '_noivos', '_coroinhas')

# Telas da secretaria (GET)
ROTAS_SECRETARIA = ('core:secretaria', 'core:listar_fichas', 'core:listar_todas_fichas')
# Ações da secretaria sobre as fichas (POST)
ACOES_SECRETARIA = tuple(f'core:{acao}_ficha{p}' for acao in ('imprimir', 'assinar', 'remover') for p in PASTORAIS)
# Telas exclusivas da coordenação (GET)
ROTAS_COORDENACAO = (
    'core:exportar-excel', 'core:total',
    'core:dashboard_turmas_catequese', 'core:dashboard_turmas_crisma',
    'core:dashboard_turmas_catequese_adulto', 'core:dashboard_turmas_perseveranca_mej',
)


def criar_ficha():
    turma = TurmaCatequeseInfantil.objects.create(nome="1a Etapa")
    return CatequeseInfantilModel.objects.create(
        nome='Ana Souza', sexo='F', data_nascimento=date(2016, 1, 1),
        endereco='Rua X', cidade='Rio Claro', uf='SP', turma=turma,
        nome_responsavel='Maria Souza', cpf_responsavel='1', endereco_responsavel='Rua X',
    )


class GruposTest(TestCase):
    """A migração cria os grupos com as permissões certas."""

    def test_secretaria_so_acessa_secretaria(self):
        perms = set(Group.objects.get(name=GRUPO_SECRETARIA).permissions.values_list('codename', flat=True))
        self.assertEqual(perms, {'acessar_secretaria'})

    def test_coordenacao_acessa_secretaria_e_coordenacao(self):
        perms = set(Group.objects.get(name=GRUPO_COORDENACAO).permissions.values_list('codename', flat=True))
        self.assertEqual(perms, {'acessar_secretaria', 'acessar_coordenacao'})


class VisitanteTest(TestCase):
    """Visitante (não logado) é levado ao login, com ?next= para a página pedida."""

    def test_rotas_restritas_levam_ao_login(self):
        for rota in ROTAS_SECRETARIA + ROTAS_COORDENACAO:
            with self.subTest(rota=rota):
                resp = self.client.get(r(rota))
                self.assertRedirects(
                    resp, f"{r('core:coordenacao')}?next={r(rota)}", fetch_redirect_response=False,
                )

    def test_formularios_de_inscricao_sao_publicos(self):
        for rota in ('core:catequese_infantil', 'core:catequese_adulto', 'core:crisma'):
            with self.subTest(rota=rota):
                self.assertEqual(self.client.get(r(rota)).status_code, HTTPStatus.OK)

    def test_acoes_da_secretaria_levam_ao_login_e_nao_alteram_fichas(self):
        ficha = criar_ficha()
        for rota in ACOES_SECRETARIA:
            with self.subTest(rota=rota):
                resp = self.client.post(r(rota), {'ficha_id': ficha.id})
                self.assertEqual(resp.status_code, HTTPStatus.FOUND)
                self.assertTrue(resp.url.startswith(r('core:coordenacao')))
        ficha.refresh_from_db()
        self.assertFalse(ficha.ficha_impressa)
        self.assertFalse(ficha.ficha_assinada)


class UsuarioSemGrupoTest(TestCase):
    """Usuário logado sem grupo recebe "Acesso negado" em tudo que é restrito."""

    def setUp(self):
        logar(self.client, 'comum')

    def test_acesso_negado(self):
        for rota in ROTAS_SECRETARIA + ROTAS_COORDENACAO:
            with self.subTest(rota=rota):
                resp = self.client.get(r(rota))
                self.assertEqual(resp.status_code, HTTPStatus.FORBIDDEN)
                self.assertTemplateUsed(resp, '403.html')

    def test_nao_remove_ficha(self):
        ficha = criar_ficha()
        resp = self.client.post(r('core:remover_ficha'), {'ficha_id': ficha.id})
        self.assertEqual(resp.status_code, HTTPStatus.FORBIDDEN)
        self.assertTrue(CatequeseInfantilModel.objects.filter(id=ficha.id).exists())


class SecretariaTest(TestCase):
    """Secretaria acessa só as telas e ações de fichas."""

    def setUp(self):
        logar(self.client, 'secretaria', GRUPO_SECRETARIA)

    def test_acessa_telas_da_secretaria(self):
        for rota in ROTAS_SECRETARIA:
            with self.subTest(rota=rota):
                resp = self.client.get(r(rota))
                self.assertEqual(resp.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(resp, 'listar_fichas.html')

    def test_acoes_da_secretaria_sao_permitidas(self):
        ficha = criar_ficha()
        resp = self.client.post(r('core:assinar_ficha'), {'ficha_id': ficha.id})
        self.assertRedirects(resp, r('core:listar_fichas'))
        ficha.refresh_from_db()
        self.assertTrue(ficha.ficha_assinada)

        resp = self.client.post(r('core:remover_ficha'), {'ficha_id': ficha.id})
        self.assertRedirects(resp, r('core:listar_fichas'))
        self.assertFalse(CatequeseInfantilModel.objects.filter(id=ficha.id).exists())

    def test_acesso_negado_na_coordenacao(self):
        for rota in ROTAS_COORDENACAO:
            with self.subTest(rota=rota):
                resp = self.client.get(r(rota))
                self.assertEqual(resp.status_code, HTTPStatus.FORBIDDEN)

    def test_menu_mostra_so_secretaria(self):
        resp = self.client.get(r('core:index'))
        self.assertContains(resp, f'href="{r("core:secretaria")}"')
        self.assertNotContains(resp, f'href="{r("core:dashboard_turmas_catequese")}"')
        self.assertNotContains(resp, f'href="{r("core:exportar-excel")}"')
        self.assertContains(resp, f'action="{r("core:coordenacao_logout")}"')


class CoordenacaoTest(TestCase):
    """Coordenação acessa tudo: suas telas e as da secretaria."""

    def setUp(self):
        logar(self.client, 'coordenacao', GRUPO_COORDENACAO)

    def test_acessa_tudo(self):
        for rota in ROTAS_SECRETARIA + ROTAS_COORDENACAO:
            with self.subTest(rota=rota):
                self.assertEqual(self.client.get(r(rota)).status_code, HTTPStatus.OK)

    def test_acessa_formulario_da_crisma(self):
        resp = self.client.get(r('core:crisma'))
        self.assertTemplateUsed(resp, 'crisma.html')

    def test_acessa_total_de_inscricoes(self):
        resp = self.client.get(r('core:total'))
        self.assertTemplateUsed(resp, 'contador_fichas.html')

    def test_baixa_relatorio(self):
        resp = self.client.get(r('core:exportar-excel'))
        self.assertIn('attachment;', resp['Content-Disposition'])

    def test_menu_mostra_secretaria_e_coordenacao(self):
        resp = self.client.get(r('core:index'))
        self.assertContains(resp, f'href="{r("core:secretaria")}"')
        self.assertContains(resp, f'href="{r("core:dashboard_turmas_catequese")}"')
        self.assertContains(resp, f'href="{r("core:exportar-excel")}"')


class SuperusuarioTest(TestCase):
    def test_superusuario_acessa_tudo_sem_grupo(self):
        logar(self.client, 'admin', is_superuser=True)
        for rota in ROTAS_SECRETARIA + ROTAS_COORDENACAO:
            with self.subTest(rota=rota):
                self.assertEqual(self.client.get(r(rota)).status_code, HTTPStatus.OK)


class StaffSemGrupoTest(TestCase):
    """is_staff deixou de dar acesso: vale só para o /admin/."""

    def test_staff_sem_grupo_recebe_acesso_negado(self):
        logar(self.client, 'staff', is_staff=True)
        self.assertEqual(self.client.get(r('core:total')).status_code, HTTPStatus.FORBIDDEN)
        self.assertEqual(self.client.get(r('core:listar_fichas')).status_code, HTTPStatus.FORBIDDEN)


class MenuVisitanteTest(TestCase):
    def test_visitante_so_ve_entrar(self):
        resp = self.client.get(r('core:index'))
        self.assertNotContains(resp, f'href="{r("core:secretaria")}"')
        self.assertNotContains(resp, f'href="{r("core:dashboard_turmas_catequese")}"')
        self.assertContains(resp, f'href="{r("core:coordenacao")}"')


class LoginPorPerfilTest(TestCase):
    """Sem ?next=, cada perfil vai para a sua página inicial."""

    def test_secretaria_vai_para_fichas(self):
        criar_usuario('secretaria', GRUPO_SECRETARIA)
        resp = self.client.post(r('core:coordenacao'), {'username': 'secretaria', 'password': 'senha12345'})
        self.assertRedirects(resp, r('core:listar_fichas'))

    def test_coordenacao_vai_para_turmas(self):
        criar_usuario('coordenacao', GRUPO_COORDENACAO)
        resp = self.client.post(r('core:coordenacao'), {'username': 'coordenacao', 'password': 'senha12345'})
        self.assertRedirects(resp, r('core:dashboard_turmas_catequese'))

    def test_secretaria_logada_abrindo_login_vai_para_fichas(self):
        logar(self.client, 'secretaria', GRUPO_SECRETARIA)
        resp = self.client.get(r('core:coordenacao'))
        self.assertRedirects(resp, r('core:listar_fichas'))
