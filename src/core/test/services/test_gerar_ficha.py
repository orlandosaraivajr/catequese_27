import os
import tempfile
from datetime import date

from django.test import TestCase, override_settings

from core.models import CatequeseInfantilModel, TurmaCatequeseInfantil
from core.services import gerar_ficha_catequese


class GerarFichaMediaRootTest(TestCase):
    """O PDF é gerado mesmo quando a pasta MEDIA_ROOT ainda não existe (ex.: clone novo)."""

    def setUp(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        self.media_root = os.path.join(tmp_dir.name, 'media_inexistente')

        turma = TurmaCatequeseInfantil.objects.create(nome="1a Etapa - Quarta às 19:30h")
        self.ficha = CatequeseInfantilModel.objects.create(
            nome='Ana Souza', sexo='F', data_nascimento=date(2016, 6, 1),
            endereco='Rua das Flores, 123', cidade='Rio Claro', uf='SP', turma=turma,
            nome_responsavel='Maria da Silva', cpf_responsavel='123.456.789-00',
            endereco_responsavel='Rua das Flores, 123',
        )

    def test_cria_media_root_e_gera_pdf(self):
        self.assertFalse(os.path.exists(self.media_root))
        with override_settings(MEDIA_ROOT=self.media_root):
            caminho = gerar_ficha_catequese(self.ficha)

        self.assertTrue(os.path.isfile(caminho))
        self.assertEqual(os.path.dirname(caminho), self.media_root)
        with open(caminho, 'rb') as f:
            self.assertEqual(f.read(4), b'%PDF')
