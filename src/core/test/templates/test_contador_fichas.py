from datetime import date

from django.shortcuts import resolve_url as r
from django.test import TestCase

from core.models import CatequeseAdultoModel, CrismaModel, TurmaCatequeseAdulto, TurmaCrisma


class TotalCrismaPorTurmaTest(TestCase):
    """O relatório de totais agrupa as fichas da Crisma pelo nome da turma."""

    def setUp(self):
        quinta = TurmaCrisma.objects.create(nome="Quinta às 19:30h")
        sabado = TurmaCrisma.objects.create(nome="Sábado às 09h")
        for i, turma in enumerate((quinta, quinta, sabado)):
            CrismaModel.objects.create(
                nome=f"Crismando {i}", sexo='M', data_nascimento=date(2010, 1, 1),
                endereco='Rua X', cidade='Rio Claro', uf='SP', turma=turma,
            )
        self.resp = self.client.get(r('core:total'))

    def test_get(self):
        self.assertEqual(self.resp.status_code, 200)

    def test_total_crisma_por_turma(self):
        self.assertEqual(self.resp.context['total_crisma'], [
            {"titulo": "Quinta às 19:30h", "quantidade": 2},
            {"titulo": "Sábado às 09h", "quantidade": 1},
        ])


class TotalCatequeseAdultoPorTurmaTest(TestCase):
    """O relatório de totais agrupa as fichas da Catequese de Adultos pelo nome da turma."""

    def setUp(self):
        quinta = TurmaCatequeseAdulto.objects.create(nome="Quinta às 19:30h - SEM Batismo")
        sabado = TurmaCatequeseAdulto.objects.create(nome="Sábado às 09h - SEM Batismo")
        for i, turma in enumerate((sabado, sabado, sabado, quinta)):
            CatequeseAdultoModel.objects.create(
                nome=f"Catequizando {i}", sexo='M', data_nascimento=date(1990, 1, 1),
                endereco='Rua X', cidade='Rio Claro', uf='SP', estado_civil='Solteiro',
                turma=turma,
            )
        self.resp = self.client.get(r('core:total'))

    def test_total_catequese_adulto_por_turma(self):
        self.assertEqual(self.resp.context['total_catequese_adulto'], [
            {"titulo": "Sábado às 09h - SEM Batismo", "quantidade": 3},
            {"titulo": "Quinta às 19:30h - SEM Batismo", "quantidade": 1},
        ])
