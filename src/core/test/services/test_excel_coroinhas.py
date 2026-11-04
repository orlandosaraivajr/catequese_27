from datetime import date
from http import HTTPStatus
from io import BytesIO

import openpyxl
from django.shortcuts import resolve_url as r
from django.test import TestCase

from core.models import CoroinhaModel
from core.services import gerar_Workbook, gerar_Workbook_coroinhas
from core.test.acessos import GRUPO_COORDENACAO, GRUPO_SECRETARIA, logar


def criar_coroinha(nome='Ana Souza', **extra):
    return CoroinhaModel.objects.create(
        nome=nome, sexo='F', data_nascimento=date(2014, 6, 1), endereco='Rua X, 1',
        cidade='Rio Claro', uf='SP', nome_pai='José Souza', celular_pai='19 99999-0001',
        nome_mae='Maria Souza', celular_mae='19 99999-0002', nome_responsavel='Maria Souza',
        cpf_responsavel='123.456.789-00', endereco_responsavel='Rua X, 1', **extra,
    )


class PlanilhaCoroinhasTest(TestCase):
    """A planilha de coroinhas tem uma linha por inscrição, com os dados do formulário."""

    def setUp(self):
        criar_coroinha()
        criar_coroinha('Bia Lima', ficha_impressa=True)
        self.ws = gerar_Workbook_coroinhas()['Coroinhas']

    def test_cabecalho(self):
        self.assertEqual([c.value for c in self.ws[1]], [
            'Nome', 'Sexo', 'Data de Nascimento', 'Endereço', 'Cidade', 'UF',
            'Nome do Pai', 'Celular do Pai', 'Nome da Mãe', 'Celular da Mãe',
            'Nome do Responsável', 'CPF do Responsável', 'Endereço do Responsável',
            'Ficha Impressa', 'Ficha Assinada', 'Data de Registro',
        ])

    def test_uma_linha_por_inscricao(self):
        self.assertEqual([linha[0].value for linha in self.ws.iter_rows(min_row=2)], ['Ana Souza', 'Bia Lima'])

    def test_valores_da_linha(self):
        linha = [c.value for c in self.ws[2]]
        self.assertEqual(linha[:6], ['Ana Souza', 'F', '01/06/2014', 'Rua X, 1', 'Rio Claro', 'SP'])
        self.assertEqual(linha[11], '123.456.789-00')
        self.assertEqual(linha[13:15], ['Não', 'Não'])
        self.assertEqual([c.value for c in self.ws[3]][13], 'Sim')

    def test_relatorio_da_catequese_nao_inclui_coroinhas(self):
        self.assertNotIn('Coroinhas', gerar_Workbook().sheetnames)


class ExportarExcelCoroinhasViewTest(TestCase):
    def test_caminho(self):
        self.assertEqual(r('core:exportar-excel-coroinhas'), '/excel-coroinhas')

    def test_coordenacao_baixa_planilha(self):
        criar_coroinha()
        logar(self.client, 'coordenacao', GRUPO_COORDENACAO)
        resp = self.client.get(r('core:exportar-excel-coroinhas'))
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertEqual(resp['Content-Type'],
                         'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        self.assertIn('attachment; filename=relatorio_coroinhas_', resp['Content-Disposition'])
        ws = openpyxl.load_workbook(BytesIO(resp.content))['Coroinhas']
        self.assertEqual(ws['A2'].value, 'Ana Souza')

    def test_secretaria_baixa_planilha(self):
        logar(self.client, 'secretaria', GRUPO_SECRETARIA)
        resp = self.client.get(r('core:exportar-excel-coroinhas'))
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertIn('attachment; filename=relatorio_coroinhas_', resp['Content-Disposition'])

    def test_visitante_vai_para_o_login(self):
        url = r('core:exportar-excel-coroinhas')
        resp = self.client.get(url)
        self.assertRedirects(resp, f"{r('core:coordenacao')}?next={url}", fetch_redirect_response=False)


class MenuRelatorioCoroinhaTest(TestCase):
    def test_coordenacao_ve_item_abaixo_de_relatorio(self):
        logar(self.client, 'coordenacao', GRUPO_COORDENACAO)
        html = self.client.get(r('core:index')).content.decode()
        relatorio = html.index(f'href="{r("core:exportar-excel")}"')
        coroinha = html.index(f'href="{r("core:exportar-excel-coroinhas")}"')
        sair = html.index(f'action="{r("core:coordenacao_logout")}"')
        self.assertLess(relatorio, coroinha)
        self.assertLess(coroinha, sair)
        self.assertIn('Relatório Coroinha', html)

    def test_visitante_nao_ve_o_item(self):
        self.assertNotContains(self.client.get(r('core:index')), r('core:exportar-excel-coroinhas'))

    def test_secretaria_ve_o_item(self):
        logar(self.client, 'secretaria', GRUPO_SECRETARIA)
        self.assertContains(self.client.get(r('core:index')), f'href="{r("core:exportar-excel-coroinhas")}"')
