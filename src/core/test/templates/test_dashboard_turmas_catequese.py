from datetime import date
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.shortcuts import resolve_url as r
from http import HTTPStatus

from core.models import TurmaCatequeseInfantil, TurmaCrisma
from core.test.acessos import GRUPO_COORDENACAO, GRUPO_SECRETARIA, criar_usuario

User = get_user_model()


class DashboardTurmasCatequeseAcessoTest(TestCase):
    """A dashboard da coordenação é restrita a usuários staff."""

    def setUp(self):
        self.client = Client()
        self.url = r('core:dashboard_turmas_catequese')

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

    def test_rota(self):
        self.assertEqual(self.url, '/coordenacao/turmas_catequese')

    def test_staff_acessa_normalmente(self):
        criar_usuario('coordenacao', GRUPO_COORDENACAO)
        self.client.login(username='coordenacao', password='senha12345')
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(resp, 'dashboard_turmas.html')


class DashboardTurmasCatequeseListagemTest(TestCase):
    def setUp(self):
        self.client = Client()
        criar_usuario('coordenacao', GRUPO_COORDENACAO)
        self.client.login(username='coordenacao', password='senha12345')
        self.turma = TurmaCatequeseInfantil.objects.create(nome="1a Etapa - Quarta às 19:30h", idade_maxima=date(2015, 1, 1), idade_minima=date(2017, 12, 31))

    def test_lista_turma_cadastrada(self):
        resp = self.client.get(r('core:dashboard_turmas_catequese'))
        self.assertContains(resp, "1a Etapa - Quarta às 19:30h")

    def test_exibe_titulo(self):
        resp = self.client.get(r('core:dashboard_turmas_catequese'))
        self.assertContains(resp, "Turmas Catequese")
        self.assertContains(resp, "Coordenação · Catequese Infantil")

    def test_nao_lista_turmas_da_crisma(self):
        TurmaCrisma.objects.create(nome="Turma exclusiva da Crisma")
        resp = self.client.get(r('core:dashboard_turmas_catequese'))
        self.assertNotContains(resp, "Turma exclusiva da Crisma")

    def test_links_de_acao_apontam_para_rotas_da_catequese(self):
        resp = self.client.get(r('core:dashboard_turmas_catequese'))
        self.assertContains(resp, r('core:criar_turma_catequese'))
        self.assertContains(resp, r('core:editar_turma_catequese', self.turma.id))
        self.assertContains(resp, r('core:alternar_turma_catequese_ativa', self.turma.id))

    def test_menu_lateral_tem_links_das_turmas(self):
        resp = self.client.get(r('core:dashboard_turmas_catequese'))
        self.assertContains(resp, "Turmas Catequese")
        self.assertContains(resp, "Turmas Crisma")
        self.assertContains(resp, f'href="{r("core:dashboard_turmas_crisma")}"')

    def test_exibe_faixa_de_nascimento(self):
        resp = self.client.get(r('core:dashboard_turmas_catequese'))
        self.assertContains(resp, "01/01/2015 a 31/12/2017")


class CriarTurmaCatequeseTest(TestCase):
    def setUp(self):
        self.client = Client()
        criar_usuario('coordenacao', GRUPO_COORDENACAO)
        self.client.login(username='coordenacao', password='senha12345')

    def test_get_exibe_formulario(self):
        resp = self.client.get(r('core:criar_turma_catequese'))
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertIn('form', resp.context)

    def test_post_cria_turma(self):
        turmas_crisma = TurmaCrisma.objects.count()
        resp = self.client.post(r('core:criar_turma_catequese'), {
            'nome': 'Sábado às 09h',
            'ativa': 'on',
            'vagas_maximas': '',
            'idade_minima': '',
            'idade_maxima': '',
            'ordem': 0,
        }, follow=True)
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertTrue(TurmaCatequeseInfantil.objects.filter(nome='Sábado às 09h').exists())
        self.assertEqual(TurmaCrisma.objects.count(), turmas_crisma)
        self.assertRedirects(resp, r('core:dashboard_turmas_catequese'))


class EditarTurmaCatequeseTest(TestCase):
    def setUp(self):
        self.client = Client()
        criar_usuario('coordenacao', GRUPO_COORDENACAO)
        self.client.login(username='coordenacao', password='senha12345')
        self.turma = TurmaCatequeseInfantil.objects.create(nome="Turma Teste")

    def test_get_exibe_formulario_preenchido(self):
        resp = self.client.get(r('core:editar_turma_catequese', self.turma.id))
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertEqual(resp.context['form'].instance, self.turma)
        self.assertContains(resp, 'Editar turma: Turma Teste')

    def test_post_atualiza_turma(self):
        resp = self.client.post(r('core:editar_turma_catequese', self.turma.id), {
            'nome': 'Turma Renomeada', 'ativa': 'on', 'vagas_maximas': 10,
            'idade_minima': '', 'idade_maxima': '', 'ordem': 1,
        })
        self.assertRedirects(resp, r('core:dashboard_turmas_catequese'))
        self.turma.refresh_from_db()
        self.assertEqual(self.turma.nome, 'Turma Renomeada')
        self.assertEqual(self.turma.vagas_maximas, 10)

    def test_turma_inexistente_retorna_404(self):
        resp = self.client.get(r('core:editar_turma_catequese', 9999))
        self.assertEqual(resp.status_code, HTTPStatus.NOT_FOUND)


class AlternarTurmaCatequeseAtivaTest(TestCase):
    def setUp(self):
        self.client = Client()
        criar_usuario('coordenacao', GRUPO_COORDENACAO)
        self.client.login(username='coordenacao', password='senha12345')
        self.turma = TurmaCatequeseInfantil.objects.create(nome="Turma Teste", ativa=True)

    def test_get_nao_altera_turma(self):
        self.client.get(r('core:alternar_turma_catequese_ativa', self.turma.id))
        self.turma.refresh_from_db()
        self.assertTrue(self.turma.ativa)

    def test_post_desativa_turma_ativa(self):
        self.client.post(r('core:alternar_turma_catequese_ativa', self.turma.id))
        self.turma.refresh_from_db()
        self.assertFalse(self.turma.ativa)

    def test_post_reativa_turma_inativa(self):
        self.turma.ativa = False
        self.turma.save()
        self.client.post(r('core:alternar_turma_catequese_ativa', self.turma.id))
        self.turma.refresh_from_db()
        self.assertTrue(self.turma.ativa)
