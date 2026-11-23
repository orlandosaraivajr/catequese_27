import tempfile
from unittest import mock

from django.test import TestCase
from reportlab.platypus import Frame

from core.services import catequese_infantil
from core.test.services.test_gerar_ficha_crisma import textos_por_pagina
from core.test.services.test_verificacao_secretaria import fichas


class CampoBibliaTest(TestCase):
    """Só a ficha da Catequese Infantil tem, na página 1, o campo "Bíblia: ____"."""

    def setUp(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        self.media_root = tmp_dir.name

    def textos(self, nome):
        _, gerador, ficha = fichas()[nome]
        return textos_por_pagina(gerador, ficha, self.media_root)

    def test_catequese_infantil_tem_o_campo_somente_na_pagina_1(self):
        paginas = [p for p, t in self.textos('catequese_infantil') if t.startswith('Bíblia:')]
        self.assertEqual(paginas, [1])

    def test_texto_do_campo(self):
        self.assertEqual(catequese_infantil.TEXTO_CAMPO_BIBLIA, 'Bíblia: ' + '_' * 22)

    def test_demais_fichas_nao_tem_o_campo(self):
        for nome in fichas():
            if nome == 'catequese_infantil':
                continue
            with self.subTest(ficha=nome):
                self.assertFalse(any('Bíblia' in t for _, t in self.textos(nome)))

    def test_campo_fica_na_coluna_da_verificacao_da_secretaria(self):
        """Mesma coluna e mesmo ``y`` do "Documento verificado por": a 1ª linha
        coincide com "Rio Claro, ..." e o traço da secretaria vem duas linhas abaixo."""
        canvas = mock.Mock()
        with mock.patch.object(catequese_infantil, 'Frame', wraps=Frame) as frame:
            catequese_infantil.desenhar_campo_biblia(canvas, 100)
        frame.assert_called_once_with(50, 100, 190, 200)
