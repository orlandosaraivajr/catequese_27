from django.test import TestCase
from core.models import Perseveranca_MEJ_Model


class PerseverancaMEJModelTest(TestCase):
    def setUp(self):
        self.cadastro = Perseveranca_MEJ_Model.objects.create(
            nome="Ana Beatriz Souza",
            sexo="F",
            data_nascimento="2013-08-15",
            naturalidade="Araras - SP",

            nome_pai="Roberto Souza",
            nome_mae="Patrícia Souza",

            endereco="Rua do Bosque, 456",
            cidade="Araras",
            uf="SP",

            celular_pai="19977778888",
            celular_mae="19966667777",

            batizado=True,
            batizado_data="2014-09-10",
            batizado_diocese="Diocese de Limeira",
            batizado_paroquia="Paróquia Nossa Senhora do Carmo",
            batizado_celebrante="Pe. José",

            primeira_eucaristia=True,
            primeira_eucaristia_data="2022-11-21",
            primeira_eucaristia_diocese="Diocese de Limeira",
            primeira_eucaristia_paroquia="Paróquia São Judas",
            primeira_eucaristia_celebrante="Pe. André",

            horario="1",

            possui_deficiencia=True,
            descricao_deficiencia="Deficiência visual leve",

            possui_transtorno=True,
            descricao_transtorno="Ansiedade",

            medicamento_uso_continuo=True,
            descricao_medicamento="Sertralina",
            medicamento_horario="1 comprimido à noite",

            acompanhamento_psicologico=True,
            descricao_acompanhamento="Sessão quinzenal",

            nome_responsavel="Patrícia Souza",
            cpf_responsavel="111.222.333-44",
            endereco_responsavel="Rua do Bosque, 456"
        )

    # ---------- CRIAÇÃO ----------
    def test_created(self):
        self.assertTrue(Perseveranca_MEJ_Model.objects.exists())

    # ---------- STR ----------
    def test_str_model(self):
        self.assertEqual(str(self.cadastro), "Ana Beatriz Souza")

    # ---------- CAMPOS BÁSICOS ----------
    def test_nome(self):
        self.assertEqual(self.cadastro.nome, "Ana Beatriz Souza")

    def test_sexo(self):
        self.assertEqual(self.cadastro.sexo, "F")

    def test_data_nascimento(self):
        self.assertEqual(str(self.cadastro.data_nascimento), "2013-08-15")

    def test_naturalidade(self):
        self.assertEqual(self.cadastro.naturalidade, "Araras - SP")

    # ---------- PAIS ----------
    def test_nome_pai(self):
        self.assertEqual(self.cadastro.nome_pai, "Roberto Souza")

    def test_nome_mae(self):
        self.assertEqual(self.cadastro.nome_mae, "Patrícia Souza")

    # ---------- ENDEREÇO ----------
    def test_endereco(self):
        self.assertEqual(self.cadastro.endereco, "Rua do Bosque, 456")

    def test_cidade(self):
        self.assertEqual(self.cadastro.cidade, "Araras")

    def test_uf(self):
        self.assertEqual(self.cadastro.uf, "SP")

    # ---------- CONTATOS ----------
    def test_celular_pai(self):
        self.assertEqual(self.cadastro.celular_pai, "19977778888")

    def test_celular_mae(self):
        self.assertEqual(self.cadastro.celular_mae, "19966667777")

    # ---------- BATISMO ----------
    def test_batizado(self):
        self.assertTrue(self.cadastro.batizado)

    def test_batizado_data(self):
        self.assertEqual(str(self.cadastro.batizado_data), "2014-09-10")

    def test_batizado_diocese(self):
        self.assertEqual(self.cadastro.batizado_diocese, "Diocese de Limeira")

    def test_batizado_paroquia(self):
        self.assertEqual(self.cadastro.batizado_paroquia, "Paróquia Nossa Senhora do Carmo")

    def test_batizado_celebrante(self):
        self.assertEqual(self.cadastro.batizado_celebrante, "Pe. José")

    # ---------- PRIMEIRA EUCARISTIA ----------
    def test_primeira_eucaristia(self):
        self.assertTrue(self.cadastro.primeira_eucaristia)

    def test_primeira_eucaristia_data(self):
        self.assertEqual(str(self.cadastro.primeira_eucaristia_data), "2022-11-21")

    def test_primeira_eucaristia_diocese(self):
        self.assertEqual(self.cadastro.primeira_eucaristia_diocese, "Diocese de Limeira")

    def test_primeira_eucaristia_paroquia(self):
        self.assertEqual(self.cadastro.primeira_eucaristia_paroquia, "Paróquia São Judas")

    def test_primeira_eucaristia_celebrante(self):
        self.assertEqual(self.cadastro.primeira_eucaristia_celebrante, "Pe. André")

    # ---------- HORÁRIO ----------
    def test_horario(self):
        self.assertEqual(self.cadastro.horario, "1")

    # ---------- DEFICIÊNCIA ----------
    def test_possui_deficiencia(self):
        self.assertTrue(self.cadastro.possui_deficiencia)

    def test_descricao_deficiencia(self):
        self.assertEqual(self.cadastro.descricao_deficiencia, "Deficiência visual leve")

    # ---------- TRANSTORNO ----------
    def test_possui_transtorno(self):
        self.assertTrue(self.cadastro.possui_transtorno)

    def test_descricao_transtorno(self):
        self.assertEqual(self.cadastro.descricao_transtorno, "Ansiedade")

    # ---------- MEDICAMENTOS ----------
    def test_medicamento_uso_continuo(self):
        self.assertTrue(self.cadastro.medicamento_uso_continuo)

    def test_descricao_medicamento(self):
        self.assertEqual(self.cadastro.descricao_medicamento, "Sertralina")

    def test_medicamento_horario(self):
        self.assertEqual(self.cadastro.medicamento_horario, "1 comprimido à noite")

    # ---------- ACOMPANHAMENTO ----------
    def test_acompanhamento_psicologico(self):
        self.assertTrue(self.cadastro.acompanhamento_psicologico)

    def test_descricao_acompanhamento(self):
        self.assertEqual(self.cadastro.descricao_acompanhamento, "Sessão quinzenal")

    # ---------- RESPONSÁVEL ----------
    def test_nome_responsavel(self):
        self.assertEqual(self.cadastro.nome_responsavel, "Patrícia Souza")

    def test_cpf_responsavel(self):
        self.assertEqual(self.cadastro.cpf_responsavel, "111.222.333-44")

    def test_endereco_responsavel(self):
        self.assertEqual(self.cadastro.endereco_responsavel, "Rua do Bosque, 456")

    # ---------- DEFAULTS ----------
    def test_ficha_impressa_default(self):
        self.assertFalse(self.cadastro.ficha_impressa)

    def test_ficha_assinada_default(self):
        self.assertFalse(self.cadastro.ficha_assinada)
