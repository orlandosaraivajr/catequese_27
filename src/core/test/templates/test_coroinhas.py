from django.test import TestCase, Client
from django.shortcuts import resolve_url as r
from http import HTTPStatus
from core.models import CoroinhaModel 
from datetime import date

class CoroinhasGetTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.resp = self.client.get(r('core:coroinhas'))

    def test_status_code(self):
        self.assertEqual(self.resp.status_code, HTTPStatus.OK)

    def test_template_used(self):
        self.assertTemplateUsed(self.resp, 'coroinhas.html')

    def test_form_in_context(self):
        self.assertIn('form', self.resp.context)


class CoroinhasPostSuccessTest(TestCase):
    def setUp(self):
        self.client = Client()
        ano_noivo = date.today().year - 25
        ano_noiva = date.today().year - 23

        ano_nascimento = date.today().year - 10  # exemplo: criança de 10 anos

        self.valid_data = {
            "nome": "Pedro Henrique Souza",
            "sexo": "M",
            "data_nascimento": f"{ano_nascimento}-06-15",
            "endereco": "Rua São José, 321",
            "cidade": "Araras",
            "uf": "SP",
            "nome_pai": "José Carlos Souza",
            "celular_pai": "11988887777",
            "nome_mae": "Maria Aparecida Souza",
            "celular_mae": "11999996666",
            "nome_responsavel": "José Carlos Souza",
            "cpf_responsavel": "123.456.789-00",
            "endereco_responsavel": "Rua São José, 321",
        }


        self.resp = self.client.post(
            r('core:coroinhas'),
            data=self.valid_data,
            follow=True
        )

    def test_redirect(self):
        self.assertEqual(self.resp.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(self.resp, 'procure_secretaria.html')

    def test_object_created(self):
        self.assertEqual(CoroinhaModel.objects.count(), 1)


class NoivosPostFailTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.invalid_data = {
            'nome': '', 
            'data_nascimento': '2015-10-20',
            'cpf': '12345678901'
        }
        self.resp = self.client.post(
            r('core:coroinhas'),
            data=self.invalid_data
        )

    def test_status_code(self):
        # Não redireciona — volta a exibir o formulário
        self.assertEqual(self.resp.status_code, HTTPStatus.OK)

    def test_template_used(self):
        self.assertTemplateUsed(self.resp, 'coroinhas.html')

    def test_form_has_errors(self):
        self.assertTrue(self.resp.context['form'].errors)

    def test_no_object_created(self):
        self.assertEqual(CoroinhaModel.objects.count(), 0)
