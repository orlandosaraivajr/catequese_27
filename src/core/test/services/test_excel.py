from datetime import date

from django.test import TestCase

from core.models import (
    CatequeseAdultoModel, CatequeseInfantilModel, CrismaModel, Perseveranca_MEJ_Model, SementinhaModel,
    TurmaCatequeseAdulto, TurmaCatequeseInfantil, TurmaCrisma, TurmaPerseveranca_MEJ, TurmaSementinha,
)
from core.services.excel import gerar_Workbook


class ExcelCrismaTest(TestCase):
    """A planilha da Crisma exporta o nome da turma na coluna de horário."""

    def setUp(self):
        turma = TurmaCrisma.objects.create(nome="Sábado às 10:30h")
        CrismaModel.objects.create(
            nome='Ana Souza', sexo='F', data_nascimento=date(2010, 6, 1),
            endereco='Rua X', cidade='Rio Claro', uf='SP', turma=turma,
        )
        self.ws = gerar_Workbook()['Crisma']

    def test_coluna_horario_tem_nome_da_turma(self):
        cabecalho = [c.value for c in self.ws[1]]
        coluna = cabecalho.index('Horário da Crisma')
        linha = [c.value for c in self.ws[2]]
        self.assertEqual(linha[coluna], 'Sábado às 10:30h')


class ExcelCatequeseAdultoTest(TestCase):
    """A planilha da Catequese de Adultos exporta o nome da turma na coluna de horário."""

    def setUp(self):
        turma = TurmaCatequeseAdulto.objects.create(nome="Quinta às 19:30h - SEM Batismo")
        CatequeseAdultoModel.objects.create(
            nome='Ana Souza', sexo='F', data_nascimento=date(1990, 6, 1),
            endereco='Rua X', cidade='Rio Claro', uf='SP', estado_civil='Solteira', turma=turma,
        )
        self.ws = gerar_Workbook()['Catequese Adulto']

    def test_coluna_horario_tem_nome_da_turma(self):
        cabecalho = [c.value for c in self.ws[1]]
        coluna = cabecalho.index('Horário da Catequese (Adulto)')
        linha = [c.value for c in self.ws[2]]
        self.assertEqual(linha[coluna], 'Quinta às 19:30h - SEM Batismo')


class ExcelPerseverancaMejTest(TestCase):
    """A planilha da Perseverança / MEJ exporta o nome da turma na coluna de horário."""

    def setUp(self):
        turma = TurmaPerseveranca_MEJ.objects.create(nome="MEJ - 15 a 25 anos - Terça às 19:30h")
        Perseveranca_MEJ_Model.objects.create(
            nome='Ana Souza', sexo='F', data_nascimento=date(2012, 6, 1),
            endereco='Rua X', cidade='Rio Claro', uf='SP', turma=turma,
            nome_responsavel='Resp Teste', cpf_responsavel='1', endereco_responsavel='Rua X',
        )
        self.ws = gerar_Workbook()['Perseverança MEJ']

    def test_coluna_horario_tem_nome_da_turma(self):
        cabecalho = [c.value for c in self.ws[1]]
        coluna = cabecalho.index('Horário da Perseverança / MEJ')
        linha = [c.value for c in self.ws[2]]
        self.assertEqual(linha[coluna], 'MEJ - 15 a 25 anos - Terça às 19:30h')


class ExcelSementinhaTest(TestCase):
    """A Sementinha tem planilha própria, separada da Catequese Infantil."""

    def setUp(self):
        dados = dict(sexo='F', endereco='Rua X', cidade='Rio Claro', uf='SP',
                     nome_responsavel='Resp Teste', cpf_responsavel='1', endereco_responsavel='Rua X')
        SementinhaModel.objects.create(
            nome='Ana Sementinha', data_nascimento=date(2021, 6, 1),
            turma=TurmaSementinha.objects.create(nome="Sementinha - Sábado às 9:00h"), **dados,
        )
        CatequeseInfantilModel.objects.create(
            nome='Bia Catequese', data_nascimento=date(2016, 6, 1),
            turma=TurmaCatequeseInfantil.objects.create(nome="1a Etapa"), **dados,
        )
        self.wb = gerar_Workbook()

    def test_ordem_das_planilhas(self):
        self.assertEqual(self.wb.sheetnames[:3], ['Catequese Infantil', 'Sementinha', 'Crisma'])

    def test_coluna_horario_tem_nome_da_turma(self):
        ws = self.wb['Sementinha']
        cabecalho = [c.value for c in ws[1]]
        coluna = cabecalho.index('Horário da Sementinha')
        linha = [c.value for c in ws[2]]
        self.assertEqual(linha[coluna], 'Sementinha - Sábado às 9:00h')

    def test_cada_planilha_tem_so_as_suas_fichas(self):
        nomes = lambda ws: [linha[0].value for linha in ws.iter_rows(min_row=2)]
        self.assertEqual(nomes(self.wb['Sementinha']), ['Ana Sementinha'])
        self.assertEqual(nomes(self.wb['Catequese Infantil']), ['Bia Catequese'])

    def test_catequese_infantil_mantem_coluna_de_horario(self):
        cabecalho = [c.value for c in self.wb['Catequese Infantil'][1]]
        self.assertIn('Horário da Catequese', cabecalho)
