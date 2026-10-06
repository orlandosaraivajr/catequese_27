from datetime import date

from django.test import TestCase

from core.models import (
    CatequeseAdultoModel, CrismaModel, Perseveranca_MEJ_Model,
    TurmaCatequeseAdulto, TurmaCrisma, TurmaPerseveranca_MEJ,
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
