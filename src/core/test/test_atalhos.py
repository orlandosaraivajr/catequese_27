from django.test import TestCase
from django.urls import reverse as r
from http import HTTPStatus


class AtalhoIndexTest(TestCase):
    def setUp(self):
        self.url = r('atalho_index')

    def test_redirects_to_core_index(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)
        self.assertRedirects(resp, r('core:index'))

    def test_redirects_to_core_index2(self):
        resp = self.client.get(self.url, follow=True)
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(resp, 'index.html')


class AtalhoSecretariaTest(TestCase):
    def setUp(self):
        self.url = r('atalho_secretaria')

    def test_redirects_to_core_secretaria(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)
        self.assertRedirects(resp, r('core:secretaria'))

    def test_redirects_to_core_secretaria2(self):
        resp = self.client.get(self.url, follow=True)
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(resp, 'listar_fichas.html')


class AtalhoExcelTotalTest(TestCase):
    def test_redirects_to_core_exportar_excel(self):
        resp = self.client.get(r('atalho_excel'))
        self.assertRedirects(resp, r('core:exportar-excel'), fetch_redirect_response=False)

    def test_redirects_to_core_total(self):
        resp = self.client.get(r('atalho_total'))
        self.assertRedirects(resp, r('core:total'), fetch_redirect_response=False)
