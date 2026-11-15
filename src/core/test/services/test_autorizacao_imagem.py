import tempfile
from datetime import date
from unittest import mock

from django.test import TestCase, override_settings
from reportlab.pdfgen.canvas import Canvas

from core import models as m
from core.services import _common
from core.test.services.test_gerar_ficha_crisma import textos_por_pagina
from core.test.services.test_verificacao_secretaria import fichas

PAGINA_TERMO_IMAGEM = 3
FICHAS_MENOR = ('catequese_infantil', 'sementinha', 'crisma_menor', 'mej_menor', 'coroinhas')
FICHAS_MAIOR = ('crisma_maior', 'mej_maior', 'catequese_adulto')

# Trechos que o termo da Diocese de Piracicaba precisa conter em TODAS as fichas.
# Se algum teste falhar, o texto do termo mudou: confirme se foi intencional.
TRECHOS_OBRIGATORIOS = (
    'DIOCESE DE PIRACICABA',
    'CNPJ sob o nº 44.802.999/0001-68',
    'Avenida Independência, nº 1146',
    'suas paróquias, seminários diocesanos ou quaisquer outras instituições a ela vinculadas',
    'meios impressos',
    'sites, Instagram, Facebook, YouTube',
    'em todo o território nacional',
    'LGPD (Lei nº 13.709/2018)',
    'não terá efeito retroativo',
    'não implicando a obrigatoriedade de retirada de materiais já publicados',
    'cessão dos direitos de veiculação das imagens para terceiros',
    'para os mesmos fins e de forma gratuita',
)
TRECHOS_PROIBIDOS = ('44.802.999/0011-30', 'Paróquia Nossa Senhora Aparecida')
TRECHO_ECA = 'Estatuto da Criança e do Adolescente – ECA (Lei nº 8.069/90)'


class TermoAutorizacaoImagemTest(TestCase):
    """O termo de uso de imagem e voz (página 3) segue o modelo da Diocese em todas as fichas."""

    def setUp(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        self.media_root = tmp_dir.name

    def termo(self, nome):
        _, gerador, ficha = fichas()[nome]
        textos = textos_por_pagina(gerador, ficha, self.media_root)
        return ' '.join(t for pagina, t in textos if pagina == PAGINA_TERMO_IMAGEM)

    def test_texto_da_diocese_em_todas_as_fichas(self):
        for nome in fichas():
            texto = self.termo(nome)
            for trecho in TRECHOS_OBRIGATORIOS:
                with self.subTest(ficha=nome, trecho=trecho):
                    self.assertIn(trecho, texto)

    def test_texto_antigo_da_paroquia_foi_removido(self):
        for nome in fichas():
            texto = self.termo(nome)
            for trecho in TRECHOS_PROIBIDOS:
                with self.subTest(ficha=nome, trecho=trecho):
                    self.assertNotIn(trecho, texto)

    def test_eca_apenas_nos_termos_de_menores(self):
        for nome in FICHAS_MENOR:
            with self.subTest(ficha=nome):
                self.assertIn(TRECHO_ECA, self.termo(nome))
        for nome in (*FICHAS_MAIOR, 'noivos'):
            with self.subTest(ficha=nome):
                texto = self.termo(nome)
                self.assertNotIn('ECA', texto)
                self.assertNotIn('8.069', texto)

    def test_numeracao_das_clausulas_e_sequencial(self):
        self.assertEqual([c[:2] for c in _common.clausulas_autorizacao_imagem(menor=True)],
                         ['1)', '2)', '3)', '4)', '5)', '6)'])
        self.assertEqual([c[:2] for c in _common.clausulas_autorizacao_imagem(menor=False)],
                         ['1)', '2)', '3)', '4)', '5)'])

    def test_menor_responsavel_autoriza_com_dados_do_formulario(self):
        for nome in FICHAS_MENOR:
            with self.subTest(ficha=nome):
                texto = self.termo(nome)
                self.assertIn('<b>Maria Responsável</b>, inscrito(a) no CPF sob o nº 123.456.789-00', texto)
                self.assertIn('residente em Rua X', texto)
                self.assertIn('responsável legal do(a) menor <b>Ana Souza</b>, nascido(a) em', texto)
                self.assertIn('a utilizar a imagem e a voz do(a) menor', texto)
                self.assertIn('declaro que autorizo', texto)
                self.assertIn('Maria Responsável - CPF: 123.456.789-00', texto)

    def test_maior_de_idade_autoriza_a_propria_imagem(self):
        cpfs = {'crisma_maior': '123.456.789-00', 'mej_maior': '123.456.789-00',
                'catequese_adulto': '111.222.333-44'}
        for nome in FICHAS_MAIOR:
            with self.subTest(ficha=nome):
                texto = self.termo(nome)
                cpf = cpfs[nome]
                self.assertIn(f'Eu, <b>Ana Souza</b>, inscrito(a) no CPF sob o nº {cpf}', texto)
                self.assertIn('residente em Rua X, 1 - Rio Claro/SP', texto)
                self.assertIn('a utilizar a minha imagem e a minha voz', texto)
                self.assertNotIn('menor', texto)
                self.assertIn(f'Ana Souza - CPF: {cpf}', texto)

    def test_noivos_autorizam_no_plural(self):
        texto = self.termo('noivos')
        self.assertIn('Nós, <b>João Noivo</b> e <b>Maria Noiva</b>, <b>AUTORIZAMOS</b>', texto)
        self.assertIn('as nossas imagens e as nossas vozes', texto)
        self.assertIn('declaramos que autorizamos', texto)

    def test_endereco_vazio_nao_gera_trecho_residente(self):
        ficha = m.CrismaModel(
            id=2, nome='Ana Souza', sexo='F', data_nascimento=date(2011, 1, 1),
            endereco='Rua X', cidade='Rio Claro', uf='SP',
            nome_responsavel='Maria', cpf_responsavel='123', endereco_responsavel='',
        )
        abertura = _common.abertura_autorizacao_imagem_menor(ficha)
        self.assertNotIn('residente em', abertura)
        self.assertIn('CPF sob o nº 123, na qualidade de pai/mãe', abertura)

    def test_texto_cabe_na_pagina_e_assinatura_fica_abaixo_dele(self):
        """O termo inteiro cabe no Frame e a assinatura começa depois do último parágrafo."""
        for nome in fichas():
            with self.subTest(ficha=nome):
                retornos = []
                original = _common.pagina_autorizacao_imagem

                def espiao(*args, **kwargs):
                    retornos.append(original(*args, **kwargs))
                    return retornos[-1]

                modulo, gerador, ficha = fichas()[nome]
                # Termos de menor chamam a função dentro de _common; os demais, pelo próprio módulo.
                with mock.patch('core.services._common.pagina_autorizacao_imagem', side_effect=espiao), \
                     mock.patch(f'core.services.{modulo}.pagina_autorizacao_imagem', side_effect=espiao,
                                create=True), \
                     override_settings(MEDIA_ROOT=self.media_root):
                    gerador(ficha)
                self.assertEqual(len(retornos), 1)
                # A assinatura (data, linha e nome ≈ 70pt) começa em y e precisa caber acima da margem.
                self.assertGreater(retornos[0] - 70, 36)

    def test_texto_que_nao_cabe_e_detectado(self):
        canvas = Canvas(f'{self.media_root}/x.pdf')
        abertura = 'texto ' * 300  # cabe sozinho, mas empurra as cláusulas para fora da página
        with self.assertRaises(ValueError):
            _common.pagina_autorizacao_imagem(canvas, _common.CABECALHO_PATH, 842, 'T', abertura)
