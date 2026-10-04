from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.shortcuts import resolve_url as r
from http import HTTPStatus

from core.models import Turma

User = get_user_model()


class DashboardTurmasAcessoTest(TestCase):
    """A dashboard da coordenação é restrita a usuários staff."""

    def setUp(self):
        self.client = Client()
        self.url = r('core:dashboard_turmas')

    def test_anonimo_e_redirecionado_para_login(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)
        self.assertTrue(resp.url.startswith(r('core:coordenacao')))

    def test_usuario_comum_recebe_redirect(self):
        User.objects.create_user(username='comum', password='senha12345')
        self.client.login(username='comum', password='senha12345')
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)

    def test_staff_acessa_normalmente(self):
        User.objects.create_user(username='coordenacao', password='senha12345', is_staff=True)
        self.client.login(username='coordenacao', password='senha12345')
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(resp, 'dashboard_turmas.html')


class DashboardTurmasListagemTest(TestCase):
    def setUp(self):
        self.client = Client()
        User.objects.create_user(username='coordenacao', password='senha12345', is_staff=True)
        self.client.login(username='coordenacao', password='senha12345')
        self.turma = Turma.objects.create(nome="1a Etapa - Quarta às 19:30h", idade_minima=9, idade_maxima=11)

    def test_lista_turma_cadastrada(self):
        resp = self.client.get(r('core:dashboard_turmas'))
        self.assertContains(resp, "1a Etapa - Quarta às 19:30h")


class CriarTurmaTest(TestCase):
    def setUp(self):
        self.client = Client()
        User.objects.create_user(username='coordenacao', password='senha12345', is_staff=True)
        self.client.login(username='coordenacao', password='senha12345')

    def test_get_exibe_formulario(self):
        resp = self.client.get(r('core:criar_turma'))
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertIn('form', resp.context)

    def test_post_cria_turma(self):
        resp = self.client.post(r('core:criar_turma'), {
            'nome': 'Sábado às 09h',
            'ativa': 'on',
            'vagas_maximas': '',
            'idade_minima': '',
            'idade_maxima': '',
            'ordem': 0,
        }, follow=True)
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertTrue(Turma.objects.filter(nome='Sábado às 09h').exists())


class AlternarTurmaAtivaTest(TestCase):
    def setUp(self):
        self.client = Client()
        User.objects.create_user(username='coordenacao', password='senha12345', is_staff=True)
        self.client.login(username='coordenacao', password='senha12345')
        self.turma = Turma.objects.create(nome="Turma Teste", ativa=True)

    def test_post_desativa_turma_ativa(self):
        self.client.post(r('core:alternar_turma_ativa', self.turma.id))
        self.turma.refresh_from_db()
        self.assertFalse(self.turma.ativa)

    def test_post_reativa_turma_inativa(self):
        self.turma.ativa = False
        self.turma.save()
        self.client.post(r('core:alternar_turma_ativa', self.turma.id))
        self.turma.refresh_from_db()
        self.assertTrue(self.turma.ativa)
