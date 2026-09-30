from django.test import TestCase, Client
from django.urls import reverse as r
from http import HTTPStatus


class IndexRedirectTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = r('index:index')

    def test_redirects_to_core_index(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)
        self.assertRedirects(resp, r('core:index'))

    def test_redirects_to_core_index2(self):
        resp = self.client.get(self.url, follow=True)
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(resp, 'index.html')


class SecretariaRedirectTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = r('index:secretaria')

    def test_redirects_to_core__secretaria(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)
        self.assertRedirects(resp, r('core:secretaria'))

    def test_redirects_to_core_secretaria2(self):
        resp = self.client.get(self.url, follow=True)
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(resp, 'listar_fichas.html')