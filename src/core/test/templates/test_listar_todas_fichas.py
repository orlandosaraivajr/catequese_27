from django.test import TestCase, Client
from django.shortcuts import resolve_url as r
from http import HTTPStatus
from datetime import date
from core.models import CatequeseInfantilModel, TurmaCatequeseInfantil
from core.test.acessos import GRUPO_SECRETARIA, logar


# Helper para criar fichas válidas
def criar_ficha(nome="Ana", sexo="F", impresso=False):
    turma, _ = TurmaCatequeseInfantil.objects.get_or_create(
        nome="1a Etapa - Quarta às 19:30h", defaults={"idade_maxima": date(2015, 1, 1), "idade_minima": date(2017, 12, 31)}
    )
    return CatequeseInfantilModel.objects.create(
        nome=nome,
        sexo=sexo,
        data_nascimento=date(2015, 6, 1),
        endereco="Rua Teste, 123",
        cidade="Rio Claro",
        uf="SP",
        turma=turma,
        nome_responsavel="Maria da Silva",
        cpf_responsavel="123.456.789-00",
        endereco_responsavel="Rua Teste, 123",
        ficha_impressa=impresso,
    )


class ListarTodasFichasGetTest(TestCase):
    def setUp(self):
        self.client = Client()
        logar(self.client, 'secretaria', GRUPO_SECRETARIA)
        self.resp = self.client.get(r("core:listar_todas_fichas"))

    def test_status_code(self):
        self.assertEqual(self.resp.status_code, HTTPStatus.OK)

    def test_template_usado(self):
        self.assertTemplateUsed(self.resp, "listar_fichas.html")

    def test_contexto_tem_mensagem(self):
        self.assertIn("mensagem", self.resp.context)
        self.assertEqual(self.resp.context["mensagem"], "Fichas Pendentes de Impressão")

    def test_contexto_tem_fichas(self):
        self.assertIn("fichas", self.resp.context)


class ListarTodasFichasZeroRegistrosTest(TestCase):
    def setUp(self):
        self.client = Client()
        logar(self.client, 'secretaria', GRUPO_SECRETARIA)
        self.resp = self.client.get(r("core:listar_todas_fichas"))

    def test_lista_vazia(self):
        fichas = list(self.resp.context["fichas"])
        self.assertEqual(len(fichas), 0)


class ListarTodasFichasUmRegistroTest(TestCase):
    def setUp(self):
        self.client = Client()
        logar(self.client, 'secretaria', GRUPO_SECRETARIA)
        self.f1 = criar_ficha(nome="Ana")
        self.resp = self.client.get(r("core:listar_todas_fichas"))

    def test_lista_com_um(self):
        fichas = list(self.resp.context["fichas"])
        self.assertEqual(len(fichas), 1)
        self.assertIn(self.f1, fichas)


class ListarTodasFichasDoisRegistrosTest(TestCase):
    def setUp(self):
        self.client = Client()
        logar(self.client, 'secretaria', GRUPO_SECRETARIA)
        self.f1 = criar_ficha(nome="Ana")
        self.f2 = criar_ficha(nome="Bruno", sexo="M")
        self.resp = self.client.get(r("core:listar_todas_fichas"))

    def test_lista_com_dois(self):
        fichas = list(self.resp.context["fichas"])
        self.assertEqual(len(fichas), 2)
        self.assertIn(self.f1, fichas)
        self.assertIn(self.f2, fichas)
