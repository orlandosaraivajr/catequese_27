from django.test import TestCase, Client
from django.shortcuts import resolve_url as r
from http import HTTPStatus


class IndexGetTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.resp = self.client.get(r('core:index'))

    def test_status_code(self):
        self.assertEqual(self.resp.status_code, HTTPStatus.OK)

    def test_template_used(self):
        self.assertTemplateUsed(self.resp, 'index.html')

    def test_links_para_todas_as_fichas(self):
        rotas = [
            'core:catequese_infantil',
            'core:perseveranca_mej',
            'core:catequese_adulto',
            'core:crisma',
            'core:noivos',
            'core:coroinhas',
        ]
        for rota in rotas:
            with self.subTest(rota):
                self.assertContains(self.resp, f'href="{r(rota)}"')

    def test_titulos_das_opcoes(self):
        for titulo in ('Catequese Infantil', 'Perseverança / MEJ', 'Catequese Adulto',
                       'Crisma', 'Casamento', 'Coroinhas'):
            with self.subTest(titulo):
                self.assertContains(self.resp, titulo)
