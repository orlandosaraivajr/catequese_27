from django.test import TestCase, Client
from django.shortcuts import resolve_url as r
from http import HTTPStatus
from core.models import CatequeseInfantilModel, Turma
from datetime import date

class CatequeseInfantilGetTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.resp = self.client.get(r('core:catequese_infantil'))

    def test_status_code(self):
        self.assertEqual(self.resp.status_code, HTTPStatus.OK)

    def test_template_used(self):
        self.assertTemplateUsed(self.resp, 'catequese_infantil.html')

    def test_form_in_context(self):
        self.assertIn('form', self.resp.context)


class CatequeseInfantilPostSuccessTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.turma = Turma.objects.create(
            nome="Pré-Catequese - Terça às 19:30h",
            idade_maxima=date(2018, 1, 1), idade_minima=date(2020, 12, 31),
        )
        self.valid_data = {
    'nome': 'João da Silva',
    'sexo': 'M',                       # 'M' ou 'F'
    'data_nascimento': '2019-10-20',   # dentro da faixa da turma
    'naturalidade': 'Araras',

    'nome_pai': 'Carlos da Silva',
    'nome_mae': 'Mariana da Silva',

    'endereco': 'Rua das Flores, 123',
    'cidade': 'Araras',
    'uf': 'SP',

    'celular_pai': '11999999999',
    'celular_mae': '11988888888',

    # campos de batismo (opcionais — remova se não quiser enviar)
    'batizado': 'on',                  # checkbox => presença indica True
    'batizado_data': '2016-04-10',
    'batizado_diocese': 'Diocese de Limeira',
    'batizado_paroquia': 'Paróquia São João Batista',
    'batizado_celebrante': 'Pe. Antônio',

    'turma': self.turma.id,             # turma válida para a idade projetada

    # necessidades/medicação (opcionais)
    'possui_deficiencia': '',          # omita ou deixe vazio para False
    'descricao_deficiencia': '',
    'possui_transtorno': '',
    'descricao_transtorno': '',
    'medicamento_uso_continuo': '',
    'descricao_medicamento': '',
    'medicamento_horario': '',
    'acompanhamento_psicologico': '',
    'descricao_acompanhamento': '',

    # responsável (obrigatório)
    'nome_responsavel': 'Carlos da Silva',
    'cpf_responsavel': '123.456.789-00',
    'endereco_responsavel': 'Rua das Flores, 123',
}

        self.resp = self.client.post(
            r('core:catequese_infantil'),
            data=self.valid_data,
            follow=True
        )

    def test_redirect(self):
        self.assertEqual(self.resp.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(self.resp, 'procure_secretaria.html')

    def test_object_created(self):
        self.assertEqual(CatequeseInfantilModel.objects.count(), 1)


class CatequeseInfantilPostFailTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.invalid_data = {
            'nome': '', 
            'data_nascimento': '2015-10-20',
            'cpf': '12345678901'
        }
        self.resp = self.client.post(
            r('core:catequese_infantil'),
            data=self.invalid_data
        )

    def test_status_code(self):
        # Não redireciona — volta a exibir o formulário
        self.assertEqual(self.resp.status_code, HTTPStatus.OK)

    def test_template_used(self):
        self.assertTemplateUsed(self.resp, 'catequese_infantil.html')

    def test_form_has_errors(self):
        self.assertTrue(self.resp.context['form'].errors)

    def test_no_object_created(self):
        self.assertEqual(CatequeseInfantilModel.objects.count(), 0)
