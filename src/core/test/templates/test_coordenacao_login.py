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
        self.assertRedirects(resp, r('core:dashboard_turmas_catequese'))
        self.assertIn(SESSION_KEY, self.client.session)

    def test_login_respeita_parametro_next(self):
        destino = r('core:criar_turma_catequese')
        resp = self.client.post(self.url, {
            'username': 'coordenadora', 'password': 'senha12345', 'next': destino,
        })
        self.assertRedirects(resp, destino)

    def test_next_externo_e_ignorado(self):
        resp = self.client.post(self.url, {
            'username': 'coordenadora', 'password': 'senha12345', 'next': 'https://site-malicioso.com/',
        })
        self.assertRedirects(resp, r('core:dashboard_turmas_catequese'))

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
        self.assertRedirects(resp, r('core:dashboard_turmas_catequese'))

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

    def test_get_nao_faz_logout(self):
        self.client.get(self.url)
        self.assertIn(SESSION_KEY, self.client.session)

    def test_get_redireciona_para_area_da_coordenacao(self):
        resp = self.client.get(self.url)
        self.assertRedirects(resp, r('core:coordenacao'), fetch_redirect_response=False)

    def test_get_logado_acaba_no_dashboard(self):
        resp = self.client.get(self.url, follow=True)
        self.assertRedirects(resp, r('core:dashboard_turmas_catequese'))

    def test_get_anonimo_acaba_no_login(self):
        resp = Client().get(self.url, follow=True)
        self.assertRedirects(resp, r('core:coordenacao'))
        self.assertTemplateUsed(resp, 'coordenacao_login.html')

    def test_apos_logout_dashboard_exige_login(self):
        self.client.post(self.url)
        resp = self.client.get(r('core:dashboard_turmas_catequese'))
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)
        self.assertTrue(resp.url.startswith(r('core:coordenacao')))


class DashboardAreaUsuarioTest(TestCase):
    """A dashboard mostra quem está logado e o botão de sair."""

    def setUp(self):
        self.client = Client()
        User.objects.create_user(username='coordenadora', password='senha12345', is_staff=True)
        self.client.login(username='coordenadora', password='senha12345')
        self.resp = self.client.get(r('core:dashboard_turmas_catequese'))

    def test_mostra_usuario_logado(self):
        self.assertContains(self.resp, 'Conectado como <strong>coordenadora</strong>', html=False)

    def test_menu_tem_link_do_relatorio(self):
        self.assertContains(self.resp, f'href="{r("core:exportar-excel")}"')
        self.assertContains(self.resp, 'Relatório')

    def test_menu_tem_link_do_total_de_inscricoes(self):
        self.assertContains(self.resp, f'href="{r("core:total")}"')
        self.assertContains(self.resp, 'Total de Inscrições')

    def test_total_de_inscricoes_fica_entre_turmas_adulto_e_relatorio(self):
        html = self.resp.content.decode()
        adulto = html.index('Turmas Catequese Adulto')
        total = html.index('Total de Inscrições')
        relatorio = html.index(f'href="{r("core:exportar-excel")}"')
        self.assertLess(adulto, total)
        self.assertLess(total, relatorio)

    def test_link_do_relatorio_baixa_planilha(self):
        resp = self.client.get(r('core:exportar-excel'))
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertEqual(
            resp['Content-Type'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        self.assertIn('attachment; filename=relatorio_catequese_', resp['Content-Disposition'])

    def test_tem_formulario_de_logout(self):
        self.assertContains(self.resp, f'action="{r("core:coordenacao_logout")}"')

    def test_anonimo_redirecionado_com_next(self):
        client = Client()
        resp = client.get(r('core:dashboard_turmas_catequese'))
        self.assertRedirects(
            resp, f"{r('core:coordenacao')}?next={r('core:dashboard_turmas_catequese')}",
            fetch_redirect_response=False,
        )


class MenuRelatorioVisibilidadeTest(TestCase):
    """O link "Relatório" só aparece no menu para a coordenação (staff)."""

    def test_anonimo_nao_ve_link_do_relatorio(self):
        resp = Client().get(r('core:index'))
        self.assertNotContains(resp, f'href="{r("core:exportar-excel")}"')

    def test_usuario_comum_nao_ve_link_do_relatorio(self):
        User.objects.create_user(username='comum', password='senha12345')
        client = Client()
        client.login(username='comum', password='senha12345')
        resp = client.get(r('core:index'))
        self.assertNotContains(resp, f'href="{r("core:exportar-excel")}"')
