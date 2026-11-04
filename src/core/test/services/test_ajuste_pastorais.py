from datetime import date

from django.test import TestCase

from core import models as m
from core.services.ajuste_pastorais import PASTORAIS_AJUSTE, campos_perdidos, transferir_ficha


def criar_crisma(**extra):
    dados = dict(
        nome='Ana Souza', sexo='F', data_nascimento=date(2021, 6, 1), naturalidade='Rio Claro',
        nome_pai='José Souza', nome_mae='Maria Souza', endereco='Rua X, 1', cidade='Rio Claro', uf='SP',
        celular_pai='19 99999-0001', celular_mae='19 99999-0002',
        batizado=True, batizado_data=date(2021, 9, 5), batizado_diocese='Piracicaba',
        batizado_paroquia='PNSA', batizado_celebrante='Pe. João',
        possui_deficiencia=True, descricao_deficiencia='Baixa visão',
        turma=m.TurmaCrisma.objects.create(nome='Quinta às 19:30h'),
        ficha_impressa=True, ficha_assinada=True,
    )
    dados.update(extra)
    return m.CrismaModel.objects.create(**dados)


class TransferirFichaTest(TestCase):
    """A transferência copia os campos em comum, apaga a origem e deixa a ficha pendente."""

    def setUp(self):
        self.origem = criar_crisma(
            primeira_eucaristia=True, primeira_eucaristia_data=date(2030, 1, 1),
            padrinho_nome='Carlos Padrinho',
        )
        self.criado_em = self.origem.criado_em
        self.turma = m.TurmaSementinha.objects.create(nome='Sementinha - Sábado às 9:00h')
        self.nova = transferir_ficha(
            self.origem, m.SementinhaModel, self.turma,
            nome_responsavel='Maria Souza', cpf_responsavel='123.456.789-00', endereco_responsavel='Rua X, 1',
        )

    def test_ficha_criada_no_destino_e_removida_da_origem(self):
        self.assertTrue(m.SementinhaModel.objects.filter(pk=self.nova.pk).exists())
        self.assertFalse(m.CrismaModel.objects.exists())

    def test_campos_em_comum_copiados(self):
        nova = m.SementinhaModel.objects.get(pk=self.nova.pk)
        for campo, valor in {
            'nome': 'Ana Souza', 'sexo': 'F', 'data_nascimento': date(2021, 6, 1),
            'naturalidade': 'Rio Claro', 'nome_pai': 'José Souza', 'nome_mae': 'Maria Souza',
            'celular_mae': '19 99999-0002', 'batizado': True, 'batizado_paroquia': 'PNSA',
            'possui_deficiencia': True, 'descricao_deficiencia': 'Baixa visão',
        }.items():
            with self.subTest(campo=campo):
                self.assertEqual(getattr(nova, campo), valor)

    def test_mantem_data_de_cadastro(self):
        self.assertEqual(m.SementinhaModel.objects.get(pk=self.nova.pk).criado_em, self.criado_em)

    def test_turma_e_responsavel_do_destino(self):
        nova = m.SementinhaModel.objects.get(pk=self.nova.pk)
        self.assertEqual(nova.turma, self.turma)
        self.assertEqual(nova.nome_responsavel, 'Maria Souza')
        self.assertEqual(nova.cpf_responsavel, '123.456.789-00')

    def test_ficha_volta_a_ficar_pendente(self):
        nova = m.SementinhaModel.objects.get(pk=self.nova.pk)
        self.assertFalse(nova.ficha_impressa)
        self.assertFalse(nova.ficha_assinada)


class TransferirFichaAtomicaTest(TestCase):
    def test_erro_ao_salvar_mantem_a_origem(self):
        origem = criar_crisma()
        turma_errada = m.TurmaCatequeseInfantil.objects.create(nome='Turma de outra pastoral')
        with self.assertRaises(ValueError):
            transferir_ficha(origem, m.SementinhaModel, turma_errada)
        self.assertTrue(m.CrismaModel.objects.filter(pk=origem.pk).exists())
        self.assertFalse(m.SementinhaModel.objects.exists())


class TransferirEntreTodasAsPastoraisTest(TestCase):
    """Qualquer par de pastorais do ajuste funciona e preserva o nome da ficha."""

    def test_todos_os_pares(self):
        for origem, cfg_origem in PASTORAIS_AJUSTE.items():
            for destino, cfg_destino in PASTORAIS_AJUSTE.items():
                if origem == destino:
                    continue
                with self.subTest(origem=origem, destino=destino):
                    ficha = cfg_origem['modelo'].objects.create(
                        nome='Ana Souza', sexo='F', data_nascimento=date(2015, 1, 1),
                        endereco='Rua X', cidade='Rio Claro', uf='SP',
                        nome_responsavel='Maria Souza', cpf_responsavel='1', endereco_responsavel='Rua X',
                        turma=cfg_origem['turma'].objects.create(nome='Origem'),
                    )
                    nova = transferir_ficha(ficha, cfg_destino['modelo'],
                                            cfg_destino['turma'].objects.create(nome='Destino'))
                    self.assertEqual(cfg_destino['modelo'].objects.get(pk=nova.pk).nome, 'Ana Souza')
                    self.assertFalse(cfg_origem['modelo'].objects.filter(pk=ficha.pk).exists())


class CamposPerdidosTest(TestCase):
    def test_crisma_para_sementinha_lista_eucaristia_e_padrinho_preenchidos(self):
        ficha = criar_crisma(primeira_eucaristia=True, primeira_eucaristia_data=date(2030, 1, 1),
                             padrinho_nome='Carlos Padrinho')
        perdidos = dict(campos_perdidos(ficha, m.SementinhaModel))
        self.assertEqual(perdidos['Primeira eucaristia'], 'Sim')
        self.assertEqual(perdidos['Primeira eucaristia data'], '01/01/2030')
        self.assertEqual(perdidos['Padrinho nome'], 'Carlos Padrinho')

    def test_campos_vazios_nao_sao_listados(self):
        self.assertEqual(campos_perdidos(criar_crisma(), m.SementinhaModel), [])

    def test_sementinha_para_catequese_nao_perde_nada(self):
        ficha = m.SementinhaModel.objects.create(
            nome='Ana Souza', sexo='F', data_nascimento=date(2021, 1, 1), endereco='Rua X',
            cidade='Rio Claro', uf='SP', nome_responsavel='Maria Souza', cpf_responsavel='1',
            endereco_responsavel='Rua X', turma=m.TurmaSementinha.objects.create(nome='S'),
        )
        self.assertEqual(campos_perdidos(ficha, m.CatequeseInfantilModel), [])
