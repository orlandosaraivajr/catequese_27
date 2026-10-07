from datetime import date
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.shortcuts import resolve_url as r
from http import HTTPStatus

from core.models import TurmaCatequeseInfantil, TurmaCrisma
from core.test.acessos import GRUPO_COORDENACAO, GRUPO_SECRETARIA, criar_usuario

User = get_user_model()


def login_coordenacao(client):
    criar_usuario('coordenacao', GRUPO_COORDENACAO)
    client.login(username='coordenacao', password='senha12345')


class DashboardTurmasCrismaAcessoTest(TestCase):
    """A dashboard de turmas da Crisma é restrita a usuários staff."""

    def setUp(self):
        self.client = Client()
        self.url = r('core:dashboard_turmas_crisma')

    def test_rota(self):
        self.assertEqual(self.url, '/coordenacao/turmas_crisma')

    def test_anonimo_e_redirecionado_para_login(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)
        self.assertTrue(resp.url.startswith(r('core:coordenacao')))

    def test_usuario_sem_grupo_recebe_acesso_negado(self):
        User.objects.create_user(username='comum', password='senha12345')
        self.client.login(username='comum', password='senha12345')
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, HTTPStatus.FORBIDDEN)
        self.assertTemplateUsed(resp, '403.html')

    def test_secretaria_recebe_acesso_negado(self):
        criar_usuario('secretaria', GRUPO_SECRETARIA)
        self.client.login(username='secretaria', password='senha12345')
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, HTTPStatus.FORBIDDEN)

    def test_staff_acessa_normalmente(self):
        login_coordenacao(self.client)
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(resp, 'dashboard_turmas.html')

    def test_demais_rotas_exigem_staff(self):
        turma = TurmaCrisma.objects.create(nome="Quinta às 19:30h")
        for url in (r('core:criar_turma_crisma'),
                    r('core:editar_turma_crisma', turma.id),
                    r('core:alternar_turma_crisma_ativa', turma.id)):
            with self.subTest(url=url):
                resp = self.client.post(url)
                self.assertEqual(resp.status_code, HTTPStatus.FOUND)
                self.assertTrue(resp.url.startswith(r('core:coordenacao')))
        turma.refresh_from_db()
        self.assertTrue(turma.ativa)


class DashboardTurmasCrismaListagemTest(TestCase):
    def setUp(self):
        self.client = Client()
        login_coordenacao(self.client)
        self.turma = TurmaCrisma.objects.create(
            nome="Quinta às 19:30h", idade_maxima=date(2008, 1, 1), idade_minima=date(2011, 12, 31),
        )
        self.resp = self.client.get(r('core:dashboard_turmas_crisma'))

    def test_lista_turma_cadastrada(self):
        self.assertContains(self.resp, "Quinta às 19:30h")

    def test_exibe_faixa_de_nascimento(self):
        self.assertContains(self.resp, "01/01/2008 a 31/12/2011")

    def test_exibe_titulo(self):
        self.assertContains(self.resp, "Turmas Crisma")
        self.assertContains(self.resp, "Coordenação · Crisma")

    def test_nao_lista_turmas_da_catequese(self):
        TurmaCatequeseInfantil.objects.create(nome="Turma exclusiva da Catequese")
        resp = self.client.get(r('core:dashboard_turmas_crisma'))
        self.assertNotContains(resp, "Turma exclusiva da Catequese")

    def test_links_de_acao_apontam_para_rotas_da_crisma(self):
        self.assertContains(self.resp, r('core:criar_turma_crisma'))
        self.assertContains(self.resp, r('core:editar_turma_crisma', self.turma.id))
        self.assertContains(self.resp, r('core:alternar_turma_crisma_ativa', self.turma.id))

    def test_menu_lateral_marca_turmas_crisma_como_ativo(self):
        self.assertContains(
            self.resp,
            f'class="gc-menu-item ativo" href="{r("core:dashboard_turmas_crisma")}"',
        )


class CriarTurmaCrismaTest(TestCase):
    def setUp(self):
        self.client = Client()
        login_coordenacao(self.client)

    def test_get_exibe_formulario(self):
        resp = self.client.get(r('core:criar_turma_crisma'))
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertIn('form', resp.context)
        self.assertContains(resp, 'Coordenação · Crisma')
        self.assertContains(resp, f'href="{r("core:dashboard_turmas_crisma")}"')

    def test_post_cria_turma_da_crisma(self):
        turmas_catequese = TurmaCatequeseInfantil.objects.count()
        resp = self.client.post(r('core:criar_turma_crisma'), {
            'nome': 'Sábado às 09h',
            'ativa': 'on',
            'vagas_maximas': '',
            'idade_minima': '',
            'idade_maxima': '',
            'ordem': 0,
        })
        self.assertRedirects(resp, r('core:dashboard_turmas_crisma'))
        self.assertTrue(TurmaCrisma.objects.filter(nome='Sábado às 09h').exists())
        self.assertEqual(TurmaCatequeseInfantil.objects.count(), turmas_catequese)

    def test_post_invalido_nao_cria(self):
        resp = self.client.post(r('core:criar_turma_crisma'), {
            'nome': 'Faixa invertida', 'ativa': 'on', 'ordem': 0,
            'idade_maxima': '2012-01-01', 'idade_minima': '2008-01-01',
        })
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertIn('idade_minima', resp.context['form'].errors)
        self.assertFalse(TurmaCrisma.objects.filter(nome='Faixa invertida').exists())


class EditarTurmaCrismaTest(TestCase):
    def setUp(self):
        self.client = Client()
        login_coordenacao(self.client)
        self.turma = TurmaCrisma.objects.create(nome="Turma Teste")

    def test_get_exibe_formulario_preenchido(self):
        resp = self.client.get(r('core:editar_turma_crisma', self.turma.id))
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertEqual(resp.context['form'].instance, self.turma)
        self.assertContains(resp, 'Editar turma: Turma Teste')

    def test_post_atualiza_turma(self):
        resp = self.client.post(r('core:editar_turma_crisma', self.turma.id), {
            'nome': 'Turma Renomeada', 'ativa': 'on', 'vagas_maximas': 10,
            'idade_minima': '', 'idade_maxima': '', 'ordem': 1,
        })
        self.assertRedirects(resp, r('core:dashboard_turmas_crisma'))
        self.turma.refresh_from_db()
        self.assertEqual(self.turma.nome, 'Turma Renomeada')
        self.assertEqual(self.turma.vagas_maximas, 10)

    def test_turma_inexistente_retorna_404(self):
        resp = self.client.get(r('core:editar_turma_crisma', 9999))
        self.assertEqual(resp.status_code, HTTPStatus.NOT_FOUND)


class AlternarTurmaCrismaAtivaTest(TestCase):
    def setUp(self):
        self.client = Client()
        login_coordenacao(self.client)
        self.turma = TurmaCrisma.objects.create(nome="Turma Teste", ativa=True)

    def test_get_nao_altera_turma(self):
        self.client.get(r('core:alternar_turma_crisma_ativa', self.turma.id))
        self.turma.refresh_from_db()
        self.assertTrue(self.turma.ativa)

    def test_post_desativa_turma_ativa(self):
        resp = self.client.post(r('core:alternar_turma_crisma_ativa', self.turma.id))
        self.assertRedirects(resp, r('core:dashboard_turmas_crisma'))
        self.turma.refresh_from_db()
        self.assertFalse(self.turma.ativa)

    def test_post_reativa_turma_inativa(self):
        self.turma.ativa = False
        self.turma.save()
        self.client.post(r('core:alternar_turma_crisma_ativa', self.turma.id))
        self.turma.refresh_from_db()
        self.assertTrue(self.turma.ativa)
