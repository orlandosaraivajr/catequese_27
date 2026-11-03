import os
import tempfile
from datetime import date
from unittest import mock

from django.test import TestCase, override_settings
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Frame

from core.models import CrismaModel, TurmaCrisma
from core.services import gerar_ficha_crisma_maior, gerar_ficha_crisma_menor
from core.test.services.test_verificacao_secretaria import fichas


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


TITULO_DECLARACAO = 'DECLARAÇÃO DE CIÊNCIA E RESPONSABILIDADE'


def textos_por_pagina(gerador, ficha, media_root):
    """Gera o PDF e devolve [(página, texto)] de tudo o que foi escrito com drawString e Paragraph."""
    textos = []
    draw, add = Canvas.drawString, Frame.addFromList

    def espiao_draw(c, x, y, texto, *args, **kwargs):
        textos.append((c.getPageNumber(), texto))
        return draw(c, x, y, texto, *args, **kwargs)

    def espiao_add(frame, flowables, c):
        textos.extend((c.getPageNumber(), f.text) for f in flowables)
        return add(frame, flowables, c)

    with mock.patch.object(Canvas, 'drawString', espiao_draw), \
         mock.patch.object(Frame, 'addFromList', espiao_add), \
         override_settings(MEDIA_ROOT=media_root):
        gerador(ficha)
    return textos


class DeclaracaoPadrinhoCrismaTest(TestCase):
    """Só a ficha da Crisma traz a declaração sobre os requisitos do padrinho/madrinha (página 4)."""

    def setUp(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        self.media_root = tmp_dir.name
        self.ficha = CrismaModel(
            id=1, nome='Ana Souza', sexo='F', data_nascimento=date(2010, 6, 1),
            endereco='Rua X', cidade='Rio Claro', uf='SP', turma=TurmaCrisma(nome='Quinta'),
            nome_responsavel='Maria da Silva', cpf_responsavel='123.456.789-00', endereco_responsavel='Rua X',
        )

    def _pagina_4(self, gerador):
        return [t for pagina, t in textos_por_pagina(gerador, self.ficha, self.media_root) if pagina == 4]

    def test_declaracao_na_pagina_4_das_duas_fichas(self):
        for gerador in (gerar_ficha_crisma_menor, gerar_ficha_crisma_maior):
            with self.subTest(gerador=gerador.__name__):
                pagina_4 = self._pagina_4(gerador)
                self.assertIn(TITULO_DECLARACAO, pagina_4)
                texto = ' '.join(pagina_4)
                self.assertIn('Diocese de Piracicaba', texto)
                self.assertIn('ter no mínimo 16 anos', texto)
                self.assertIn('Não poderá ser pai, mãe ou cônjuge do crismando', texto)

    def test_assinatura_tem_nome_e_cpf_do_responsavel(self):
        for gerador in (gerar_ficha_crisma_menor, gerar_ficha_crisma_maior):
            with self.subTest(gerador=gerador.__name__):
                texto = ' '.join(self._pagina_4(gerador))
                self.assertIn('Maria da Silva - CPF: 123.456.789-00', texto)
                self.assertNotIn('Assinatura do Responsável', texto)

    def test_demais_fichas_nao_tem_a_declaracao(self):
        for nome, (_, gerador, ficha) in fichas().items():
            if nome.startswith('crisma'):
                continue
            with self.subTest(ficha=nome):
                textos = [t for _, t in textos_por_pagina(gerador, ficha, self.media_root)]
                self.assertNotIn(TITULO_DECLARACAO, textos)


class SacramentosPrimeiraPaginaCrismaTest(TestCase):
    """A primeira página da ficha da Crisma mostra os dados do Batismo e da Primeira Eucaristia."""

    def setUp(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        self.media_root = tmp_dir.name

    def _ficha(self, **kwargs):
        return CrismaModel(
            id=1, nome='Ana Souza', sexo='F', data_nascimento=date(2010, 6, 1),
            endereco='Rua X', cidade='Rio Claro', uf='SP', turma=TurmaCrisma(nome='Quinta'),
            nome_responsavel='Maria da Silva', cpf_responsavel='123.456.789-00', endereco_responsavel='Rua X',
            **kwargs,
        )

    def _pagina_1(self, gerador, ficha):
        return [t for pagina, t in textos_por_pagina(gerador, ficha, self.media_root) if pagina == 1]

    def test_com_batismo_e_eucaristia(self):
        ficha = self._ficha(
            batizado=True, batizado_data=date(2010, 9, 5), batizado_diocese='Diocese de Piracicaba',
            batizado_paroquia='PNSA', batizado_celebrante='Pe. João',
            primeira_eucaristia=True, primeira_eucaristia_data=date(2019, 11, 10),
            primeira_eucaristia_diocese='Diocese de Limeira', primeira_eucaristia_paroquia='São Benedito',
            primeira_eucaristia_celebrante='Pe. Pedro',
        )
        for gerador in (gerar_ficha_crisma_menor, gerar_ficha_crisma_maior):
            with self.subTest(gerador=gerador.__name__):
                textos = self._pagina_1(gerador, ficha)
                for esperado in ('Batizado', 'Data: 05/09/2010', 'Diocese: Diocese de Piracicaba',
                                 'Paróquia: PNSA', 'Celebrante: Pe. João',
                                 'Primeira Eucaristia', 'Data: 10/11/2019', 'Diocese: Diocese de Limeira',
                                 'Paróquia: São Benedito', 'Celebrante: Pe. Pedro'):
                    self.assertIn(esperado, textos)

    def test_sem_batismo_e_sem_eucaristia(self):
        for gerador in (gerar_ficha_crisma_menor, gerar_ficha_crisma_maior):
            with self.subTest(gerador=gerador.__name__):
                textos = self._pagina_1(gerador, self._ficha())
                self.assertIn('Não Batizado', textos)
                self.assertIn('Não Fez Primeira Eucaristia', textos)
