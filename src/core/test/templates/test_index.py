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
        for titulo in ('Catequese Infantil', 'MEJ', 'Catequese Adulto',
                       'Crisma', 'Casamento', 'Coroinhas'):
            with self.subTest(titulo):
                self.assertContains(self.resp, titulo)


class RotasMejTest(TestCase):
    """As rotas do MEJ usam /mej no caminho (antes /perseveranca)."""

    def test_caminhos(self):
        esperado = {
            'core:perseveranca_mej': '/mej',
            'core:imprimir_ficha_perseveranca_mej': '/imprimir-ficha-mej',
            'core:assinar_ficha_perseveranca_mej': '/assinar-ficha-mej',
            'core:remover_ficha_perseveranca_mej': '/remover-ficha-mej',
            'core:dashboard_turmas_perseveranca_mej': '/coordenacao/turmas_mej',
        }
        for rota, caminho in esperado.items():
            with self.subTest(rota):
                self.assertEqual(r(rota), caminho)

    def test_caminho_antigo_nao_existe(self):
        self.assertEqual(self.client.get('/perseveranca').status_code, 404)
