from django.test import TestCase, Client
from django.urls import reverse
from django.shortcuts import resolve_url as r
from django.http import FileResponse
from unittest.mock import patch
from datetime import date
import os
import tempfile

from core.models import CatequeseInfantilModel, TurmaCatequeseInfantil, SementinhaModel, TurmaSementinha
from core.test.acessos import GRUPO_SECRETARIA, logar


# Helper para criar ficha válida
def criar_ficha():
    turma = TurmaCatequeseInfantil.objects.create(nome="1a Etapa - Quarta às 19:30h", idade_maxima=date(2015, 1, 1), idade_minima=date(2017, 12, 31))
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
        logar(self.client, 'secretaria', GRUPO_SECRETARIA)
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
        logar(self.client, 'secretaria', GRUPO_SECRETARIA)
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

        # Diretório temporário multiplataforma (Windows/Linux), removido ao final
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        pdf_path = os.path.join(tmp_dir.name, "ficha_teste.pdf")

        # Criar arquivo fake
        with open(pdf_path, "wb") as f:
            f.write(b"PDF TESTE")

        # O mock retorna o caminho do PDF fake
        mock_pdf.return_value = pdf_path

        resp = self.client.post(self.url, {"ficha_id": self.ficha.id})
        # Fecha o arquivo aberto pelo FileResponse (no Windows, arquivo aberto não pode ser apagado)
        self.addCleanup(resp.close)

        # --- Verificar se a view retornou um FileResponse ---
        self.assertIsInstance(resp, FileResponse)

        # --- Forçar reload do objeto do banco ---
        self.ficha.refresh_from_db()
        self.assertTrue(self.ficha.ficha_impressa)

        # --- Verificar se gerar_ficha_catequese foi chamado uma vez ---
        mock_pdf.assert_called_once_with(self.ficha)


class ImprimirFichaSementinhaPostTest(TestCase):
    def setUp(self):
        self.client = Client()
        logar(self.client, 'secretaria', GRUPO_SECRETARIA)
        turma = TurmaSementinha.objects.create(nome="Sementinha - Sábado às 9:00h")
        self.ficha = SementinhaModel.objects.create(
            nome='Ana Souza', sexo='F', data_nascimento=date(2021, 6, 1),
            endereco='Rua das Flores, 123', cidade='Araras', uf='SP', turma=turma,
            nome_responsavel='Maria da Silva', cpf_responsavel='123.456.789-00',
            endereco_responsavel='Rua das Flores, 123',
        )

    def test_get_redireciona_para_listagem(self):
        resp = self.client.get(r("core:imprimir_ficha_sementinha"))
        self.assertRedirects(resp, r("core:listar_fichas"), fetch_redirect_response=False)

    @patch("core.views.gerar_ficha_sementinha")
    def test_post_marca_como_impressa(self, mock_pdf):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        pdf_path = os.path.join(tmp_dir.name, "ficha_teste.pdf")
        with open(pdf_path, "wb") as f:
            f.write(b"PDF TESTE")
        mock_pdf.return_value = pdf_path

        resp = self.client.post(r("core:imprimir_ficha_sementinha"), {"ficha_id": self.ficha.id})
        self.addCleanup(resp.close)

        self.assertIsInstance(resp, FileResponse)
        self.ficha.refresh_from_db()
        self.assertTrue(self.ficha.ficha_impressa)
        mock_pdf.assert_called_once_with(self.ficha)

    def test_assinar_marca_como_assinada(self):
        resp = self.client.post(r("core:assinar_ficha_sementinha"), {"ficha_id": self.ficha.id})
        self.assertRedirects(resp, r("core:listar_fichas"), fetch_redirect_response=False)
        self.ficha.refresh_from_db()
        self.assertTrue(self.ficha.ficha_assinada)

    def test_remover_apaga_ficha(self):
        resp = self.client.post(r("core:remover_ficha_sementinha"), {"ficha_id": self.ficha.id})
        self.assertRedirects(resp, r("core:listar_fichas"), fetch_redirect_response=False)
        self.assertFalse(SementinhaModel.objects.filter(id=self.ficha.id).exists())

    def test_ficha_inexistente_retorna_404(self):
        resp = self.client.post(r("core:imprimir_ficha_sementinha"), {"ficha_id": 9999})
        self.assertEqual(resp.status_code, 404)
