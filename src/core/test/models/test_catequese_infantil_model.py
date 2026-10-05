from datetime import date
from django.test import TestCase
from core.models import CatequeseInfantilModel, TurmaCatequeseInfantil


class CatequeseInfantilModelTest(TestCase):
    def setUp(self):
        self.turma = TurmaCatequeseInfantil.objects.create(nome="1a Etapa - Quarta às 19:30h", idade_maxima=date(2015, 1, 1), idade_minima=date(2017, 12, 31))
        self.cadastro = CatequeseInfantilModel.objects.create(
            nome="João da Silva",
            sexo="M",
            data_nascimento="2015-03-10",
            naturalidade="Araras - SP",

            nome_pai="Carlos da Silva",
            nome_mae="Mariana da Silva",

            endereco="Rua das Flores, 123",
            cidade="Araras",
            uf="SP",

            celular_pai="19999999999",
            celular_mae="19988888888",

            batizado=True,
            batizado_data="2016-04-10",
            batizado_diocese="Diocese de Limeira",
            batizado_paroquia="Paróquia São João Batista",
            batizado_celebrante="Pe. Antônio",

            turma=self.turma,

            possui_deficiencia=True,
            descricao_deficiencia="Deficiência auditiva leve",

            possui_transtorno=True,
            descricao_transtorno="TDAH",

            medicamento_uso_continuo=True,
            descricao_medicamento="Ritalina",
            medicamento_horario="1 comprimido pela manhã",

            acompanhamento_psicologico=True,
            descricao_acompanhamento="Acompanhamento semanal",

            nome_responsavel="Carlos da Silva",
            cpf_responsavel="123.456.789-00",
            endereco_responsavel="Rua das Flores, 123"
        )

    def test_created(self):
        self.assertTrue(CatequeseInfantilModel.objects.exists())

    def test_str_model(self):
        self.assertEqual(str(self.cadastro), "João da Silva")

    def test_nome(self):
        self.assertEqual(self.cadastro.nome, "João da Silva")

    def test_sexo(self):
        self.assertEqual(self.cadastro.sexo, "M")

    def test_data_nascimento(self):
        self.assertEqual(str(self.cadastro.data_nascimento), "2015-03-10")

    def test_naturalidade(self):
        self.assertEqual(self.cadastro.naturalidade, "Araras - SP")

    def test_nome_pai(self):
        self.assertEqual(self.cadastro.nome_pai, "Carlos da Silva")

    def test_nome_mae(self):
        self.assertEqual(self.cadastro.nome_mae, "Mariana da Silva")

    def test_endereco(self):
        self.assertEqual(self.cadastro.endereco, "Rua das Flores, 123")

    def test_cidade(self):
        self.assertEqual(self.cadastro.cidade, "Araras")

    def test_uf(self):
        self.assertEqual(self.cadastro.uf, "SP")

    def test_celular_pai(self):
        self.assertEqual(self.cadastro.celular_pai, "19999999999")

    def test_celular_mae(self):
        self.assertEqual(self.cadastro.celular_mae, "19988888888")

    # ---------- BATISMO ----------
    def test_batizado(self):
        self.assertTrue(self.cadastro.batizado)

    def test_batizado_data(self):
        self.assertEqual(str(self.cadastro.batizado_data), "2016-04-10")

    def test_batizado_diocese(self):
        self.assertEqual(self.cadastro.batizado_diocese, "Diocese de Limeira")

    def test_batizado_paroquia(self):
        self.assertEqual(self.cadastro.batizado_paroquia, "Paróquia São João Batista")

    def test_batizado_celebrante(self):
        self.assertEqual(self.cadastro.batizado_celebrante, "Pe. Antônio")

    # ---------- TURMA ----------
    def test_turma(self):
        self.assertEqual(self.cadastro.turma, self.turma)

    # ---------- DEFICIÊNCIA ----------
    def test_possui_deficiencia(self):
        self.assertTrue(self.cadastro.possui_deficiencia)

    def test_descricao_deficiencia(self):
        self.assertEqual(self.cadastro.descricao_deficiencia, "Deficiência auditiva leve")

    # ---------- TRANSTORNO ----------
    def test_possui_transtorno(self):
        self.assertTrue(self.cadastro.possui_transtorno)

    def test_descricao_transtorno(self):
        self.assertEqual(self.cadastro.descricao_transtorno, "TDAH")

    # ---------- MEDICAMENTOS ----------
    def test_medicamento_uso_continuo(self):
        self.assertTrue(self.cadastro.medicamento_uso_continuo)

    def test_descricao_medicamento(self):
        self.assertEqual(self.cadastro.descricao_medicamento, "Ritalina")

    def test_medicamento_horario(self):
        self.assertEqual(self.cadastro.medicamento_horario, "1 comprimido pela manhã")

    # ---------- ACOMPANHAMENTO ----------
    def test_acompanhamento_psicologico(self):
        self.assertTrue(self.cadastro.acompanhamento_psicologico)

    def test_descricao_acompanhamento(self):
        self.assertEqual(self.cadastro.descricao_acompanhamento, "Acompanhamento semanal")

    # ---------- RESPONSÁVEL ----------
    def test_nome_responsavel(self):
        self.assertEqual(self.cadastro.nome_responsavel, "Carlos da Silva")

    def test_cpf_responsavel(self):
        self.assertEqual(self.cadastro.cpf_responsavel, "123.456.789-00")

    def test_endereco_responsavel(self):
        self.assertEqual(self.cadastro.endereco_responsavel, "Rua das Flores, 123")

    def test_ficha_impressa_default(self):
        self.assertFalse(self.cadastro.ficha_impressa)