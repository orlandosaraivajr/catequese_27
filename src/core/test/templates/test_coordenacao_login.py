from django.contrib.auth import get_user_model, SESSION_KEY
from django.test import TestCase, Client
from django.shortcuts import resolve_url as r
from http import HTTPStatus

User = get_user_model()


class CoordenacaoLoginGetTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.resp = self.client.get(r('core:coordenacao'))

    def test_status_200(self):
        self.assertEqual(self.resp.status_code, HTTPStatus.OK)

    def test_template(self):
        self.assertTemplateUsed(self.resp, 'coordenacao_login.html')

    def test_html(self):
        for esperado in ('csrfmiddlewaretoken', 'name="username"', 'name="password"', 'type="submit"'):
            with self.subTest(esperado):
                self.assertContains(self.resp, esperado)


class CoordenacaoLoginPostTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = r('core:coordenacao')
        User.objects.create_user(username='coordenadora', password='senha12345', is_staff=True)
        User.objects.create_user(username='comum', password='senha12345')

    def test_staff_faz_login_e_vai_para_dashboard(self):
        resp = self.client.post(self.url, {'username': 'coordenadora', 'password': 'senha12345'})
        self.assertRedirects(resp, r('core:dashboard_turmas'))
        self.assertIn(SESSION_KEY, self.client.session)

    def test_login_respeita_parametro_next(self):
        destino = r('core:criar_turma')
        resp = self.client.post(self.url, {
            'username': 'coordenadora', 'password': 'senha12345', 'next': destino,
        })
        self.assertRedirects(resp, destino)

    def test_next_externo_e_ignorado(self):
        resp = self.client.post(self.url, {
            'username': 'coordenadora', 'password': 'senha12345', 'next': 'https://site-malicioso.com/',
        })
        self.assertRedirects(resp, r('core:dashboard_turmas'))

    def test_senha_errada_nao_loga(self):
        resp = self.client.post(self.url, {'username': 'coordenadora', 'password': 'errada'})
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertTrue(resp.context['form'].errors)
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_usuario_nao_staff_nao_loga(self):
        resp = self.client.post(self.url, {'username': 'comum', 'password': 'senha12345'})
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertContains(resp, 'não tem acesso à área da coordenação')
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_usuario_inativo_nao_loga(self):
        User.objects.create_user(username='inativa', password='senha12345', is_staff=True, is_active=False)
        resp = self.client.post(self.url, {'username': 'inativa', 'password': 'senha12345'})
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertNotIn(SESSION_KEY, self.client.session)


class CoordenacaoLoginJaAutenticadoTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_staff_logado_e_redirecionado_para_dashboard(self):
        User.objects.create_user(username='coordenadora', password='senha12345', is_staff=True)
        self.client.login(username='coordenadora', password='senha12345')
        resp = self.client.get(r('core:coordenacao'))
        self.assertRedirects(resp, r('core:dashboard_turmas'))

    def test_nao_staff_logado_ve_formulario_sem_loop(self):
        User.objects.create_user(username='comum', password='senha12345')
        self.client.login(username='comum', password='senha12345')
        resp = self.client.get(r('core:coordenacao'))
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertContains(resp, 'Entre com outro usuário')


class CoordenacaoLogoutTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = r('core:coordenacao_logout')
        User.objects.create_user(username='coordenadora', password='senha12345', is_staff=True)
        self.client.login(username='coordenadora', password='senha12345')

    def test_post_faz_logout_e_volta_para_login(self):
        resp = self.client.post(self.url)
        self.assertRedirects(resp, r('core:coordenacao'))
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_get_nao_permitido(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, HTTPStatus.METHOD_NOT_ALLOWED)
        self.assertIn(SESSION_KEY, self.client.session)

    def test_apos_logout_dashboard_exige_login(self):
        self.client.post(self.url)
        resp = self.client.get(r('core:dashboard_turmas'))
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)
        self.assertTrue(resp.url.startswith(r('core:coordenacao')))


class DashboardAreaUsuarioTest(TestCase):
    """A dashboard mostra quem está logado e o botão de sair."""

    def setUp(self):
        self.client = Client()
        User.objects.create_user(username='coordenadora', password='senha12345', is_staff=True)
        self.client.login(username='coordenadora', password='senha12345')
        self.resp = self.client.get(r('core:dashboard_turmas'))

    def test_mostra_usuario_logado(self):
        self.assertContains(self.resp, 'Conectado como <strong>coordenadora</strong>', html=False)

    def test_tem_formulario_de_logout(self):
        self.assertContains(self.resp, f'action="{r("core:coordenacao_logout")}"')

    def test_anonimo_redirecionado_com_next(self):
        client = Client()
        resp = client.get(r('core:dashboard_turmas'))
        self.assertRedirects(
            resp, f"{r('core:coordenacao')}?next={r('core:dashboard_turmas')}",
            fetch_redirect_response=False,
        )
