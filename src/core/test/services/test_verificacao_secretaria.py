import tempfile
from datetime import date
from unittest import mock

from django.test import TestCase, override_settings

from core import models as m
from core import services
from core.services import _common

BASE = dict(nome='Ana Souza', sexo='F', endereco='Rua X, 1', cidade='Rio Claro', uf='SP',
            nome_pai='Pai Teste', nome_mae='Mae Teste')
RESPONSAVEL = dict(nome_responsavel='Maria Responsável', cpf_responsavel='123.456.789-00',
                   endereco_responsavel='Rua X')


def fichas():
    """Uma ficha (não salva) de cada tipo, com o gerador de PDF correspondente."""
    return {
        'catequese_infantil': (
            'catequese_infantil', services.gerar_ficha_catequese,
            m.CatequeseInfantilModel(id=1, data_nascimento=date(2016, 1, 1),
                                     turma=m.TurmaCatequeseInfantil(nome='1a Etapa'), **BASE, **RESPONSAVEL)),
        'crisma_menor': (
            'crisma', services.gerar_ficha_crisma_menor,
            m.CrismaModel(id=2, data_nascimento=date(2011, 1, 1),
                          turma=m.TurmaCrisma(nome='Quinta'), **BASE, **RESPONSAVEL)),
        'crisma_maior': (
            'crisma', services.gerar_ficha_crisma_maior,
            m.CrismaModel(id=3, data_nascimento=date(2006, 1, 1),
                          turma=m.TurmaCrisma(nome='Quinta'), **BASE, **RESPONSAVEL)),
        'mej_menor': (
            'perseveranca_mej', services.gerar_ficha_perseveranca_mej_menor_idade,
            m.Perseveranca_MEJ_Model(id=4, data_nascimento=date(2012, 1, 1),
                                     turma=m.TurmaPerseveranca_MEJ(nome='MEJ'), **BASE, **RESPONSAVEL)),
        'mej_maior': (
            'perseveranca_mej', services.gerar_ficha_perseveranca_mej_maior_idade,
            m.Perseveranca_MEJ_Model(id=5, data_nascimento=date(2000, 1, 1),
                                     turma=m.TurmaPerseveranca_MEJ(nome='MEJ'), **BASE, **RESPONSAVEL)),
        'catequese_adulto': (
            'catequese_adulto', services.gerar_ficha_catequese_adulto,
            m.CatequeseAdultoModel(id=6, cpf='111.222.333-44', data_nascimento=date(1990, 1, 1),
                                   estado_civil='Solteira', turma=m.TurmaCatequeseAdulto(nome='Quinta'), **BASE)),
        'coroinhas': (
            'coroinhas', services.gerar_ficha_coroinhas,
            m.CoroinhaModel(id=7, nome='Ana Souza', sexo='F', data_nascimento=date(2014, 1, 1),
                            endereco='Rua X', cidade='Rio Claro', uf='SP', **RESPONSAVEL)),
        'noivos': (
            'noivos', services.gerar_ficha_noivos,
            m.NoivoModel(id=8, nome_noivo='João Noivo', nome_noiva='Maria Noiva',
                         data_nascimento_noivo=date(1995, 1, 1), data_nascimento_noiva=date(1996, 1, 1),
                         data_provavel_casamento=date(2027, 5, 1), paroquia_casamento='PNSA')),
    }


class VerificacaoSecretariaTest(TestCase):
    """Toda página com assinatura tem, ao lado, o campo "Documento verificado por"."""

    def setUp(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        self.media_root = tmp_dir.name

    def _paginas_com_verificacao(self, modulo, gerador, ficha):
        """Gera o PDF e devolve as páginas em que o campo da secretaria foi desenhado."""
        paginas = []
        original = _common.desenhar_verificacao_secretaria

        def espiao(c, *args, **kwargs):
            paginas.append(c.getPageNumber())
            return original(c, *args, **kwargs)

        # Os termos compartilhados (LGPD / imagem de menores) chamam a função dentro de _common.
        with mock.patch(f'core.services.{modulo}.desenhar_verificacao_secretaria', side_effect=espiao), \
             mock.patch('core.services._common.desenhar_verificacao_secretaria', side_effect=espiao), \
             override_settings(MEDIA_ROOT=self.media_root):
            caminho = gerador(ficha)
        with open(caminho, 'rb') as f:
            self.assertEqual(f.read(4), b'%PDF')
        return paginas

    def test_campo_em_todas_as_paginas_de_todas_as_fichas(self):
        for nome, (modulo, gerador, ficha) in fichas().items():
            with self.subTest(ficha=nome):
                self.assertEqual(self._paginas_com_verificacao(modulo, gerador, ficha), [1, 2, 3])

    def test_texto_do_campo(self):
        canvas = mock.Mock()
        with mock.patch.object(_common, 'Frame') as frame:
            _common.desenhar_verificacao_secretaria(canvas, 100)
        paragrafo = frame.return_value.addFromList.call_args.args[0][0]
        self.assertIn('Documento verificado por', paragrafo.text)
        frame.assert_called_once_with(50, 100, 190, 200)
