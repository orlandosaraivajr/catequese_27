from django.test import TestCase
from datetime import date
from core.models import CrismaModel


class CrismaModelTest(TestCase):
    def setUp(self):
        self.registro = CrismaModel.objects.create(
            nome="Maria de Lourdes",
            sexo="F",
            data_nascimento="2010-05-20",
            naturalidade="Limeira - SP",

            nome_pai="João de Souza",
            nome_mae="Ana de Souza",

            endereco="Rua Central, 500",
            cidade="Araras",
            uf="SP",

            celular_pai="19977775555",
            celular_mae="19966664444",

            batizado=True,
            batizado_data="2011-06-20",
            batizado_diocese="Diocese de Limeira",
            batizado_paroquia="Paróquia Santo Antônio",
            batizado_celebrante="Pe. Ricardo",

            primeira_eucaristia=True,
            primeira_eucaristia_data="2018-09-15",
            primeira_eucaristia_diocese="Diocese de Limeira",
            primeira_eucaristia_paroquia="Paróquia Santo Antônio",
            primeira_eucaristia_celebrante="Pe. Marcos",

            horario="1",

            padrinho_nome="Carlos Henrique",
            padrinho_celular="19955553333",
        )

    # -----------------------------
    # REGISTRO E STR
    # -----------------------------
    def test_created(self):
        self.assertTrue(CrismaModel.objects.exists())

    def test_str(self):
        self.assertEqual(str(self.registro), "Maria de Lourdes")

    # -----------------------------
    # CAMPOS PRINCIPAIS
    # -----------------------------
    def test_nome(self):
        self.assertEqual(self.registro.nome, "Maria de Lourdes")

    def test_sexo(self):
        self.assertEqual(self.registro.sexo, "F")

    def test_data_nascimento(self):
        self.assertEqual(str(self.registro.data_nascimento), "2010-05-20")

    def test_naturalidade(self):
        self.assertEqual(self.registro.naturalidade, "Limeira - SP")

    # -----------------------------
    # PAIS
    # -----------------------------
    def test_nome_pai(self):
        self.assertEqual(self.registro.nome_pai, "João de Souza")

    def test_nome_mae(self):
        self.assertEqual(self.registro.nome_mae, "Ana de Souza")

    # -----------------------------
    # ENDEREÇO
    # -----------------------------
    def test_endereco(self):
        self.assertEqual(self.registro.endereco, "Rua Central, 500")

    def test_cidade(self):
        self.assertEqual(self.registro.cidade, "Araras")

    def test_uf(self):
        self.assertEqual(self.registro.uf, "SP")

    # -----------------------------
    # CELULARES
    # -----------------------------
    def test_celular_pai(self):
        self.assertEqual(self.registro.celular_pai, "19977775555")

    def test_celular_mae(self):
        self.assertEqual(self.registro.celular_mae, "19966664444")

    # -----------------------------
    # BATIZADO
    # -----------------------------
    def test_batizado(self):
        self.assertTrue(self.registro.batizado)

    def test_batizado_data(self):
        self.assertEqual(str(self.registro.batizado_data), "2011-06-20")

    def test_batizado_diocese(self):
        self.assertEqual(self.registro.batizado_diocese, "Diocese de Limeira")

    def test_batizado_paroquia(self):
        self.assertEqual(self.registro.batizado_paroquia, "Paróquia Santo Antônio")

    def test_batizado_celebrante(self):
        self.assertEqual(self.registro.batizado_celebrante, "Pe. Ricardo")

    # -----------------------------
    # PRIMEIRA EUCARISTIA
    # -----------------------------
    def test_primeira_eucaristia(self):
        self.assertTrue(self.registro.primeira_eucaristia)

    def test_primeira_eucaristia_data(self):
        self.assertEqual(str(self.registro.primeira_eucaristia_data), "2018-09-15")

    def test_primeira_eucaristia_diocese(self):
        self.assertEqual(self.registro.primeira_eucaristia_diocese, "Diocese de Limeira")

    def test_primeira_eucaristia_paroquia(self):
        self.assertEqual(self.registro.primeira_eucaristia_paroquia, "Paróquia Santo Antônio")

    def test_primeira_eucaristia_celebrante(self):
        self.assertEqual(self.registro.primeira_eucaristia_celebrante, "Pe. Marcos")

    # -----------------------------
    # HORÁRIO
    # -----------------------------
    def test_horario(self):
        self.assertEqual(self.registro.horario, "1")

    # -----------------------------
    # PADRINHO
    # -----------------------------
    def test_padrinho_nome(self):
        self.assertEqual(self.registro.padrinho_nome, "Carlos Henrique")

    def test_padrinho_celular(self):
        self.assertEqual(self.registro.padrinho_celular, "19955553333")

    # -----------------------------
    # FICHA IMPRESSA
    # -----------------------------
    def test_ficha_impressa_default_false(self):
        novo = CrismaModel.objects.create(
            nome="Teste",
            sexo="M",
            data_nascimento="2010-01-01",
            endereco="Rua A",
            cidade="Araras",
            uf="SP",
            horario="1",
        )
        self.assertFalse(novo.ficha_impressa)
