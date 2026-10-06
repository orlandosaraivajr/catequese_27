from datetime import date

from django.test import TestCase
from core.models import Perseveranca_MEJ_Model, TurmaPerseveranca_MEJ


class TurmaPerseveranca_MEJModelTest(TestCase):
    def setUp(self):
        self.turma = TurmaPerseveranca_MEJ.objects.create(
            nome="Perseverança e MEJ - 11 a 14 anos - Quinta às 19:30h - Encontros na Capela NSGraças",
            idade_maxima=date(2011, 1, 1),
            idade_minima=date(2014, 12, 31),
            vagas_maximas=2,
        )

    def test_created(self):
        self.assertTrue(TurmaPerseveranca_MEJ.objects.exists())

    def test_faixa_de_nascimento_e_date(self):
        self.turma.refresh_from_db()
        self.assertEqual(self.turma.idade_maxima, date(2011, 1, 1))
        self.assertEqual(self.turma.idade_minima, date(2014, 12, 31))

    def test_faixa_de_nascimento_opcional(self):
        turma_livre = TurmaPerseveranca_MEJ.objects.create(nome="Transferência")
        self.assertIsNone(turma_livre.idade_minima)
        self.assertIsNone(turma_livre.idade_maxima)

    def test_str_model(self):
        self.assertEqual(str(self.turma), "Perseverança e MEJ - 11 a 14 anos - Quinta às 19:30h - Encontros na Capela NSGraças")

    def test_ativa_default(self):
        self.assertTrue(self.turma.ativa)

    def test_ordem_default(self):
        self.assertEqual(self.turma.ordem, 0)

    def test_vagas_ocupadas_sem_inscritos(self):
        self.assertEqual(self.turma.vagas_ocupadas, 0)

    def test_vagas_disponiveis_sem_limite(self):
        turma_livre = TurmaPerseveranca_MEJ.objects.create(nome="Transferência")
        self.assertIsNone(turma_livre.vagas_disponiveis)

    def test_lotada_false_quando_ha_vaga(self):
        self.assertFalse(self.turma.lotada)

    def test_lotada_true_quando_atinge_limite(self):
        for i in range(2):
            Perseveranca_MEJ_Model.objects.create(
                nome=f"Jovem {i}", sexo="F", data_nascimento=date(2012, 1, 1),
                endereco="Rua X", cidade="Rio Claro", uf="SP", turma=self.turma,
                nome_responsavel="Responsável Teste", cpf_responsavel="123.456.789-00",
                endereco_responsavel="Rua X",
            )
        self.turma.refresh_from_db()
        self.assertEqual(self.turma.vagas_ocupadas, 2)
        self.assertEqual(self.turma.vagas_disponiveis, 0)
        self.assertTrue(self.turma.lotada)
