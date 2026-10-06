from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.shortcuts import resolve_url as r
from django.test import TestCase, Client

User = get_user_model()

# Rotas restritas à coordenação (staff).
ROTAS_RESTRITAS = ('core:crisma', 'core:exportar-excel')


class AcessoRestritoAnonimoTest(TestCase):
    def test_anonimo_vai_para_login_da_coordenacao(self):
        for rota in ROTAS_RESTRITAS:
            with self.subTest(rota=rota):
                resp = Client().get(r(rota))
                self.assertRedirects(
                    resp, f"{r('core:coordenacao')}?next={r(rota)}",
                    fetch_redirect_response=False,
                )


class AcessoRestritoUsuarioComumTest(TestCase):
    def setUp(self):
        User.objects.create_user(username='comum', password='senha12345')
        self.client.login(username='comum', password='senha12345')

    def test_usuario_sem_staff_nao_acessa(self):
        for rota in ROTAS_RESTRITAS:
            with self.subTest(rota=rota):
                resp = self.client.get(r(rota))
                self.assertEqual(resp.status_code, HTTPStatus.FOUND)
                self.assertTrue(resp.url.startswith(r('core:coordenacao')))


class AcessoRestritoStaffTest(TestCase):
    def setUp(self):
        User.objects.create_user(username='coordenacao', password='senha12345', is_staff=True)
        self.client.login(username='coordenacao', password='senha12345')

    def test_staff_acessa_formulario_da_crisma(self):
        resp = self.client.get(r('core:crisma'))
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(resp, 'crisma.html')

    def test_staff_baixa_relatorio(self):
        resp = self.client.get(r('core:exportar-excel'))
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertIn('attachment;', resp['Content-Disposition'])
