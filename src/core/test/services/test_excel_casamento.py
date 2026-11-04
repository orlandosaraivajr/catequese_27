from datetime import date
from http import HTTPStatus
from io import BytesIO

import openpyxl
from django.shortcuts import resolve_url as r
from django.test import TestCase

from core.models import NoivoModel
from core.services import gerar_Workbook, gerar_Workbook_casamento
from core.test.acessos import GRUPO_COORDENACAO, GRUPO_SECRETARIA, logar


def criar_noivos(nome_noivo='João Pereira', **extra):
    dados = {}
    for pessoa, nome in (('noivo', nome_noivo), ('noiva', 'Maria Lima')):
        dados.update({
            f'nome_{pessoa}': nome, f'endereco_{pessoa}': f'Rua {pessoa}, 1',
            f'celular_{pessoa}': f'19 9999-{pessoa}', f'data_nascimento_{pessoa}': date(1995, 3, 4),
            f'profissao_{pessoa}': 'Professor', f'local_trabalho_{pessoa}': 'Escola',
            f'religiao_{pessoa}': 'Católica', f'restricao_alimentar_{pessoa}': 'Nenhuma',
            f'nome_pai_{pessoa}': f'Pai {pessoa}', f'nome_mae_{pessoa}': f'Mãe {pessoa}',
            f'endereco_pais_{pessoa}': 'Rua Pais', f'celular_pais_{pessoa}': '19 8888',
            f'religiao_pais_{pessoa}': 'Católica',
        })
    dados.update(data_provavel_casamento=date(2027, 5, 15), paroquia_casamento='PNSA', **extra)
    return NoivoModel.objects.create(**dados)


class PlanilhaCasamentoTest(TestCase):
    """A planilha de casamento tem uma linha por casal, com os dados do noivo e da noiva."""

    def setUp(self):
        criar_noivos()
        criar_noivos('Pedro Alves', ficha_impressa=True)
        self.ws = gerar_Workbook_casamento()['Casamento']
        self.cabecalho = [c.value for c in self.ws[1]]

    def test_cabecalho(self):
        self.assertEqual(self.cabecalho[0], 'Nome (Noivo)')
        self.assertEqual(self.cabecalho[13], 'Nome (Noiva)')
        self.assertEqual(self.cabecalho[-5:], [
            'Data Provável do Casamento', 'Paróquia do Casamento',
            'Ficha Impressa', 'Ficha Assinada', 'Data de Registro',
        ])
        self.assertEqual(len(self.cabecalho), 31)

    def test_uma_linha_por_casal(self):
        self.assertEqual([linha[0].value for linha in self.ws.iter_rows(min_row=2)], ['João Pereira', 'Pedro Alves'])

    def test_valores_da_linha(self):
        linha = dict(zip(self.cabecalho, [c.value for c in self.ws[2]]))
        self.assertEqual(linha['Nome (Noiva)'], 'Maria Lima')
        self.assertEqual(linha['Celular (Noivo)'], '19 9999-noivo')
        self.assertEqual(linha['Data de Nascimento (Noiva)'], '04/03/1995')
        self.assertEqual(linha['Religião dos Pais (Noivo)'], 'Católica')
        self.assertEqual(linha['Data Provável do Casamento'], '15/05/2027')
        self.assertEqual(linha['Paróquia do Casamento'], 'PNSA')
        self.assertEqual(linha['Ficha Impressa'], 'Não')
        self.assertEqual(dict(zip(self.cabecalho, [c.value for c in self.ws[3]]))['Ficha Impressa'], 'Sim')

    def test_relatorio_da_catequese_nao_inclui_casamento(self):
        self.assertNotIn('Casamento', gerar_Workbook().sheetnames)


class ExportarExcelCasamentoViewTest(TestCase):
    def test_caminho(self):
        self.assertEqual(r('core:exportar-excel-casamento'), '/excel-casamento')

    def test_coordenacao_baixa_planilha(self):
        criar_noivos()
        logar(self.client, 'coordenacao', GRUPO_COORDENACAO)
        resp = self.client.get(r('core:exportar-excel-casamento'))
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertEqual(resp['Content-Type'],
                         'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        self.assertIn('attachment; filename=relatorio_casamento_', resp['Content-Disposition'])
        ws = openpyxl.load_workbook(BytesIO(resp.content))['Casamento']
        self.assertEqual(ws['A2'].value, 'João Pereira')

    def test_secretaria_baixa_planilha(self):
        logar(self.client, 'secretaria', GRUPO_SECRETARIA)
        resp = self.client.get(r('core:exportar-excel-casamento'))
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertIn('attachment; filename=relatorio_casamento_', resp['Content-Disposition'])

    def test_visitante_vai_para_o_login(self):
        url = r('core:exportar-excel-casamento')
        resp = self.client.get(url)
        self.assertRedirects(resp, f"{r('core:coordenacao')}?next={url}", fetch_redirect_response=False)


class MenuRelatorioCasamentoTest(TestCase):
    def test_coordenacao_ve_item_logo_abaixo_de_relatorio(self):
        logar(self.client, 'coordenacao', GRUPO_COORDENACAO)
        html = self.client.get(r('core:index')).content.decode()
        relatorio = html.index(f'href="{r("core:exportar-excel")}"')
        casamento = html.index(f'href="{r("core:exportar-excel-casamento")}"')
        coroinha = html.index(f'href="{r("core:exportar-excel-coroinhas")}"')
        self.assertLess(relatorio, casamento)
        self.assertLess(casamento, coroinha)
        self.assertIn('Relatório Casamento', html)

    def test_visitante_nao_ve_o_item(self):
        self.assertNotContains(self.client.get(r('core:index')), r('core:exportar-excel-casamento'))

    def test_secretaria_ve_o_item(self):
        logar(self.client, 'secretaria', GRUPO_SECRETARIA)
        self.assertContains(self.client.get(r('core:index')), f'href="{r("core:exportar-excel-casamento")}"')
