from django.test import TestCase, Client
from django.urls import reverse
from django.shortcuts import resolve_url as r
from django.http import FileResponse
from unittest.mock import patch
from datetime import date

from core.models import CatequeseInfantilModel, Turma


# Helper para criar ficha válida
def criar_ficha():
    turma = Turma.objects.create(nome="1a Etapa - Quarta às 19:30h", idade_minima=9, idade_maxima=11)
    return CatequeseInfantilModel.objects.create(
        nome='Ana',
        sexo='F',
        data_nascimento=date(2015, 6, 1),
        endereco='Rua das Flores, 123',
        cidade='Araras',
        uf='SP',
        turma=turma,
        nome_responsavel='Maria da Silva',
        cpf_responsavel='123.456.789-00',
        endereco_responsavel='Rua das Flores, 123',
        ficha_impressa=False,
    )


# ------------------------------------------------------------
#                  TESTES PARA GET
# ------------------------------------------------------------
class ImprimirFichaGetTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = r("core:imprimir_ficha")
        self.resp = self.client.get(self.url)

    def test_redirect(self):
        self.assertEqual(self.resp.status_code, 302)
        self.assertEqual(self.resp.url, r("core:listar_fichas"))


# ------------------------------------------------------------
#                TESTES PARA POST (com mock)
# ------------------------------------------------------------
class ImprimirFichaPostTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.ficha = criar_ficha()
        self.url = r("core:imprimir_ficha")

    @patch("core.views.gerar_ficha_catequese")
    def test_post_marca_como_impressa(self, mock_pdf):
        """
        O teste verifica:
        - se a função gerar_ficha_catequese foi chamada
        - se ficha_impressa foi marcada como True
        - se foi retornado um FileResponse
        """

        # O mock retorna um caminho fake de PDF
        mock_pdf.return_value = "/tmp/ficha_teste.pdf"

        # Criar arquivo fake
        with open("/tmp/ficha_teste.pdf", "wb") as f:
            f.write(b"PDF TESTE")

        resp = self.client.post(self.url, {"ficha_id": self.ficha.id})

        # --- Verificar se a view retornou um FileResponse ---
        self.assertIsInstance(resp, FileResponse)

        # --- Forçar reload do objeto do banco ---
        self.ficha.refresh_from_db()
        self.assertTrue(self.ficha.ficha_impressa)

        # --- Verificar se gerar_ficha_catequese foi chamado uma vez ---
        mock_pdf.assert_called_once_with(self.ficha)
