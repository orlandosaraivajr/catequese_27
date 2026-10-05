from datetime import date

from django.test import TestCase

from core.models import CrismaModel, TurmaCrisma
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
