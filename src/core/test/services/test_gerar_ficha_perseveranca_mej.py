import tempfile
from datetime import date

from django.test import TestCase, override_settings

from core.models import Perseveranca_MEJ_Model, TurmaPerseveranca_MEJ
from core.services import (
    gerar_ficha_perseveranca_mej_maior_idade,
    gerar_ficha_perseveranca_mej_menor_idade,
)


class GerarFichaPerseverancaMejTest(TestCase):
    """As fichas da Perseverança / MEJ (menor e maior de idade) usam o nome da turma no horário."""

    def setUp(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        self.media_root = tmp_dir.name

        turma = TurmaPerseveranca_MEJ.objects.create(nome="MEJ - 15 a 25 anos - Quinta às 19:30h")
        self.ficha = Perseveranca_MEJ_Model.objects.create(
            nome='Ana Souza', sexo='F', data_nascimento=date(2012, 6, 1),
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
        self._assert_pdf(gerar_ficha_perseveranca_mej_menor_idade)

    def test_gera_pdf_maior(self):
        self._assert_pdf(gerar_ficha_perseveranca_mej_maior_idade)
