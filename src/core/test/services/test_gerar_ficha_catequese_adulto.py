import tempfile
from datetime import date

from django.test import TestCase, override_settings

from core.models import CatequeseAdultoModel, TurmaCatequeseAdulto
from core.services import gerar_ficha_catequese_adulto


class GerarFichaCatequeseAdultoTest(TestCase):
    """A ficha da Catequese de Adultos usa o nome da turma no horário."""

    def setUp(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        self.media_root = tmp_dir.name

        turma = TurmaCatequeseAdulto.objects.create(nome="Quinta às 19:30h - SEM Batismo")
        self.ficha = CatequeseAdultoModel.objects.create(
            nome='Ana Souza', cpf='123.456.789-00', sexo='F', data_nascimento=date(1990, 6, 1),
            endereco='Rua das Flores, 123', cidade='Rio Claro', uf='SP', estado_civil='Solteira',
            turma=turma,
        )

    def test_gera_pdf(self):
        with override_settings(MEDIA_ROOT=self.media_root):
            caminho = gerar_ficha_catequese_adulto(self.ficha)
        with open(caminho, 'rb') as f:
            self.assertEqual(f.read(4), b'%PDF')
