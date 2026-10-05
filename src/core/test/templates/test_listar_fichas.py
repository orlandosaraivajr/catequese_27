from django.test import TestCase, Client
from django.shortcuts import resolve_url as r
from http import HTTPStatus
from core.models import CatequeseInfantilModel, TurmaCatequeseInfantil
from datetime import date


class ListarFichasGetTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = r('core:listar_fichas')

    def test_status_code(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, HTTPStatus.OK)

    def test_template_used(self):
        resp = self.client.get(self.url)
        self.assertTemplateUsed(resp, 'listar_fichas.html')

    def test_context_contains_mensagem(self):
        resp = self.client.get(self.url)
        self.assertIn('mensagem', resp.context)
        self.assertEqual(resp.context['mensagem'], 'Fichas Pendentes de Impressão')


# ---------------------------
#   TESTES DE LISTAGEM
# ---------------------------

class ListarFichasSemRegistrosTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = r('core:listar_fichas')
        self.resp = self.client.get(self.url)

    def test_lista_vazia(self):
        fichas = self.resp.context['fichas']
        self.assertEqual(list(fichas), [])  # deve estar vazio


class ListarFichasUmRegistroTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = r('core:listar_fichas')
        self.turma = TurmaCatequeseInfantil.objects.create(nome="1a Etapa - Quarta às 19:30h", idade_maxima=date(2015, 1, 1), idade_minima=date(2017, 12, 31))

        # Ficha pendente de impressão
        self.f1 = CatequeseInfantilModel.objects.create(
            nome='Ana',
            sexo='F',
            data_nascimento=date(2015, 6, 1),
            endereco='Rua das Flores, 123',
            cidade='Araras',
            uf='SP',
            turma=self.turma,
            nome_responsavel='Maria da Silva',
            cpf_responsavel='123.456.789-00',
            endereco_responsavel='Rua das Flores, 123',
            ficha_impressa=False,
        )

        self.resp = self.client.get(self.url)

    def test_lista_com_um_registro(self):
        fichas = list(self.resp.context['fichas'])
        self.assertEqual(len(fichas), 1)
        self.assertIn(self.f1, fichas)


class ListarFichasDoisRegistrosTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = r('core:listar_fichas')
        self.turma = TurmaCatequeseInfantil.objects.create(nome="1a Etapa - Quarta às 19:30h", idade_maxima=date(2015, 1, 1), idade_minima=date(2017, 12, 31))

        # Ficha pendente (deve aparecer)
        self.f1 = CatequeseInfantilModel.objects.create(
            nome='Ana',
            sexo='F',
            data_nascimento=date(2015, 6, 1),
            endereco='Rua das Flores, 123',
            cidade='Araras',
            uf='SP',
            turma=self.turma,
            nome_responsavel='Maria da Silva',
            cpf_responsavel='123.456.789-00',
            endereco_responsavel='Rua das Flores, 123',
            ficha_impressa=False,
        )

        # Ficha já impressa (NÃO deve aparecer)
        self.f2 = CatequeseInfantilModel.objects.create(
            nome='Carlos',
            sexo='M',
            data_nascimento=date(2015, 6, 1),
            endereco='Rua das Flores, 123',
            cidade='Araras',
            uf='SP',
            turma=self.turma,
            nome_responsavel='Maria da Silva',
            cpf_responsavel='123.456.789-00',
            endereco_responsavel='Rua das Flores, 123',
            ficha_impressa=True,
        )

        self.resp = self.client.get(self.url)

    def test_somente_nao_impressas_listadas(self):
        fichas = list(self.resp.context['fichas'])

        self.assertIn(self.f1, fichas)   # deve estar
        self.assertNotIn(self.f2, fichas)  # não deve estar

    def test_quantidade_uma_ficha(self):
        fichas = list(self.resp.context['fichas'])
        self.assertEqual(len(fichas), 1)
