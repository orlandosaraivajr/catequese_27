from django.test import TestCase
from core.models import CatequeseAdultoModel


class CatequeseAdultoModelTest(TestCase):

    def setUp(self):
        self.cadastro = CatequeseAdultoModel.objects.create(
            nome="Maria de Lourdes Silva",
            cpf="123.456.789-00",
            sexo="F",
            data_nascimento="1990-08-15",
            naturalidade="Araras - SP",

            celular="19999990000",

            nome_pai="José da Silva",
            nome_mae="Ana de Lourdes",

            endereco="Av. Brasil, 500",
            cidade="Araras",
            uf="SP",
            estado_civil="Solteira",

            # Batismo
            batizado=True,
            batizado_data="1991-09-20",
            batizado_diocese="Diocese de Limeira",
            batizado_paroquia="Paróquia São José",
            batizado_celebrante="Pe. João",

            # Primeira Eucaristia
            primeira_eucaristia=True,
            primeira_eucaristia_data="2000-10-10",
            primeira_eucaristia_diocese="Diocese de Limeira",
            primeira_eucaristia_paroquia="Paróquia São José",
            primeira_eucaristia_celebrante="Pe. João",

            # Casamento na Igreja
            casado_igreja=False,

            horario="1",

            padrinho_nome="Carlos Mendes",
            padrinho_celular="19977776666",
        )

    # ----------------- CRIAÇÃO -----------------
    def test_created(self):
        self.assertTrue(CatequeseAdultoModel.objects.exists())

    def test_str_model(self):
        self.assertEqual(str(self.cadastro), "Maria de Lourdes Silva")

    # ----------------- DADOS PESSOAIS -----------------
    def test_nome(self):
        self.assertEqual(self.cadastro.nome, "Maria de Lourdes Silva")

    def test_cpf(self):
        self.assertEqual(self.cadastro.cpf, "123.456.789-00")

    def test_sexo(self):
        self.assertEqual(self.cadastro.sexo, "F")

    def test_data_nascimento(self):
        self.assertEqual(str(self.cadastro.data_nascimento), "1990-08-15")

    def test_naturalidade(self):
        self.assertEqual(self.cadastro.naturalidade, "Araras - SP")

    def test_celular(self):
        self.assertEqual(self.cadastro.celular, "19999990000")

    def test_nome_pai(self):
        self.assertEqual(self.cadastro.nome_pai, "José da Silva")

    def test_nome_mae(self):
        self.assertEqual(self.cadastro.nome_mae, "Ana de Lourdes")

    def test_endereco(self):
        self.assertEqual(self.cadastro.endereco, "Av. Brasil, 500")

    def test_cidade(self):
        self.assertEqual(self.cadastro.cidade, "Araras")

    def test_uf(self):
        self.assertEqual(self.cadastro.uf, "SP")

    def test_estado_civil(self):
        self.assertEqual(self.cadastro.estado_civil, "Solteira")

    # ----------------- BATISMO -----------------
    def test_batizado(self):
        self.assertTrue(self.cadastro.batizado)

    def test_batizado_data(self):
        self.assertEqual(str(self.cadastro.batizado_data), "1991-09-20")

    def test_batizado_diocese(self):
        self.assertEqual(self.cadastro.batizado_diocese, "Diocese de Limeira")

    def test_batizado_paroquia(self):
        self.assertEqual(self.cadastro.batizado_paroquia, "Paróquia São José")

    def test_batizado_celebrante(self):
        self.assertEqual(self.cadastro.batizado_celebrante, "Pe. João")

    # ----------------- 1ª EUCARISTIA -----------------
    def test_primeira_eucaristia(self):
        self.assertTrue(self.cadastro.primeira_eucaristia)

    def test_primeira_eucaristia_data(self):
        self.assertEqual(str(self.cadastro.primeira_eucaristia_data), "2000-10-10")

    def test_primeira_eucaristia_diocese(self):
        self.assertEqual(self.cadastro.primeira_eucaristia_diocese, "Diocese de Limeira")

    def test_primeira_eucaristia_paroquia(self):
        self.assertEqual(self.cadastro.primeira_eucaristia_paroquia, "Paróquia São José")

    def test_primeira_eucaristia_celebrante(self):
        self.assertEqual(self.cadastro.primeira_eucaristia_celebrante, "Pe. João")

    # ----------------- CASAMENTO NA IGREJA -----------------
    def test_casado_igreja(self):
        self.assertFalse(self.cadastro.casado_igreja)

    def test_casado_igreja_data_default(self):
        self.assertIsNone(self.cadastro.casado_igreja_data)

    # ----------------- HORÁRIO -----------------
    def test_horario(self):
        self.assertEqual(self.cadastro.horario, "1")

    # ----------------- PADRINHOS -----------------
    def test_padrinho_nome(self):
        self.assertEqual(self.cadastro.padrinho_nome, "Carlos Mendes")

    def test_padrinho_celular(self):
        self.assertEqual(self.cadastro.padrinho_celular, "19977776666")

    # ----------------- DEFAULTS -----------------
    def test_ficha_impressa_default(self):
        self.assertFalse(self.cadastro.ficha_impressa)

    def test_ficha_assinada_default(self):
        self.assertFalse(self.cadastro.ficha_assinada)
