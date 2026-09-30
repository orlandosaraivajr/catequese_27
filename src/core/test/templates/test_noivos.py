from django.test import TestCase, Client
from django.shortcuts import resolve_url as r
from http import HTTPStatus
from core.models import NoivoModel 
from datetime import date

class NoivosGetTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.resp = self.client.get(r('core:noivos'))

    def test_status_code(self):
        self.assertEqual(self.resp.status_code, HTTPStatus.OK)

    def test_template_used(self):
        self.assertTemplateUsed(self.resp, 'noivos.html')

    def test_form_in_context(self):
        self.assertIn('form', self.resp.context)


class NoivosPostSuccessTest(TestCase):
    def setUp(self):
        self.client = Client()
        ano_noivo = date.today().year - 25
        ano_noiva = date.today().year - 23

        self.valid_data = {
            # =========================
            # NOIVO
            # =========================
            "nome_noivo": "João da Silva",
            "endereco_noivo": "Rua das Flores, 123",
            "celular_noivo": "11999999999",
            "data_nascimento_noivo": f"{ano_noivo}-05-10",
            "profissao_noivo": "Analista de Sistemas",
            "local_trabalho_noivo": "Empresa XYZ",
            "religiao_noivo": "Católica",
            "restricao_alimentar_noivo": "Nenhuma",
            "nome_pai_noivo": "Carlos da Silva",
            "nome_mae_noivo": "Mariana da Silva",
            "endereco_pais_noivo": "Rua das Flores, 123",
            "celular_pais_noivo": "11988888888",
            "religiao_pais_noivo": "Católica",

            # =========================
            # NOIVA
            # =========================
            "nome_noiva": "Maria Aparecida",
            "endereco_noiva": "Rua das Acácias, 456",
            "celular_noiva": "11977777777",
            "data_nascimento_noiva": f"{ano_noiva}-08-22",
            "profissao_noiva": "Professora",
            "local_trabalho_noiva": "Escola Estadual Central",
            "religiao_noiva": "Católica",
            "restricao_alimentar_noiva": "Nenhuma",
            "nome_pai_noiva": "José Pereira",
            "nome_mae_noiva": "Ana Pereira",
            "endereco_pais_noiva": "Rua das Acácias, 456",
            "celular_pais_noiva": "11966666666",
            "religiao_pais_noiva": "Católica",

            # =========================
            # CASAMENTO
            # =========================
            "data_provavel_casamento": f"{date.today().year + 1}-10-10",
            "paroquia_casamento": "Paróquia São João Batista",
        }

        self.resp = self.client.post(
            r('core:noivos'),
            data=self.valid_data,
            follow=True
        )

    def test_redirect(self):
        self.assertEqual(self.resp.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(self.resp, 'procure_secretaria.html')

    def test_object_created(self):
        self.assertEqual(NoivoModel.objects.count(), 1)


class NoivosPostFailTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.invalid_data = {
            'nome': '', 
            'data_nascimento': '2015-10-20',
            'cpf': '12345678901'
        }
        self.resp = self.client.post(
            r('core:noivos'),
            data=self.invalid_data
        )

    def test_status_code(self):
        # Não redireciona — volta a exibir o formulário
        self.assertEqual(self.resp.status_code, HTTPStatus.OK)

    def test_template_used(self):
        self.assertTemplateUsed(self.resp, 'noivos.html')

    def test_form_has_errors(self):
        self.assertTrue(self.resp.context['form'].errors)

    def test_no_object_created(self):
        self.assertEqual(NoivoModel.objects.count(), 0)
