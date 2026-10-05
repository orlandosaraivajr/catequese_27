import os
import tempfile
from datetime import date

from django.test import TestCase, override_settings

from core.models import CrismaModel, TurmaCrisma
from core.services import gerar_ficha_crisma_maior, gerar_ficha_crisma_menor


class GerarFichaCrismaTest(TestCase):
    """As fichas da Crisma (menor e maior de idade) usam o nome da turma no horário."""

    def setUp(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        self.media_root = tmp_dir.name

        turma = TurmaCrisma.objects.create(nome="Quinta às 19:30h")
        self.ficha = CrismaModel.objects.create(
            nome='Ana Souza', sexo='F', data_nascimento=date(2010, 6, 1),
            endereco='Rua das Flores, 123', cidade='Rio Claro', uf='SP', turma=turma,
            nome_responsavel='Maria da Silva', cpf_responsavel='123.456.789-00',
            endereco_responsavel='Rua das Flores, 123',
        )

    def _assert_pdf(self, gerador):
        with override_settings(MEDIA_ROOT=self.media_root):
            caminho = gerador(self.ficha)
        with open(caminho, 'rb') as f:
            self.assertEqual(f.read(4), b'%PDF')

    def test_gera_pdf_menor(self):
        self._assert_pdf(gerar_ficha_crisma_menor)

    def test_gera_pdf_maior(self):
        self._assert_pdf(gerar_ficha_crisma_maior)
