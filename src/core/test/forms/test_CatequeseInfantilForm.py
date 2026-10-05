import datetime
from django.test import TestCase
from core.models import CatequeseInfantilModel, TurmaCatequeseInfantil
from core.forms import CatequeseInfantilForm


class CatequeseInfantilFormTurmaTests(TestCase):

    def setUp(self):
        # Pré-Catequese: nascidos entre 01/01/2018 e 31/12/2020
        self.turma_pre = TurmaCatequeseInfantil.objects.create(
            nome="Pré-Catequese - Terça às 19:30h",
            idade_maxima=datetime.date(2018, 1, 1), idade_minima=datetime.date(2020, 12, 31),
        )
        # 1a Etapa: nascidos entre 01/01/2015 e 31/12/2017
        self.turma_1a_etapa = TurmaCatequeseInfantil.objects.create(
            nome="1a Etapa - Quarta às 19:30h",
            idade_maxima=datetime.date(2015, 1, 1), idade_minima=datetime.date(2017, 12, 31),
        )
        self.turma_sem_restricao = TurmaCatequeseInfantil.objects.create(nome="Transferência")
        self.turma_inativa = TurmaCatequeseInfantil.objects.create(nome="Turma Encerrada", ativa=False)

        self.valid_base_data = {
            'nome': 'Maria Silva',
            'sexo': 'F',
            'data_nascimento': datetime.date(2018, 5, 10),
            'naturalidade': 'São Paulo',

            'nome_pai': 'João da Silva',
            'nome_mae': 'Ana da Silva',

            'endereco': 'Rua teste',
            'cidade': 'SP',
            'uf': 'SP',

            'celular_pai': '1199999',
            'celular_mae': '1199999',

            'batizado': False,

            'turma': self.turma_pre.id,  # será substituído a cada teste

            'possui_deficiencia': False,
            'possui_transtorno': False,
            'medicamento_uso_continuo': False,
            'acompanhamento_psicologico': False,

            'nome_responsavel': 'Maria Souza',
            'cpf_responsavel': '00011122233',
            'endereco_responsavel': 'Rua teste'
        }

    # ------------------------------------
    # helper
    # ------------------------------------
    def make_form(self, **kwargs):
        data = self.valid_base_data.copy()
        data.update(kwargs)
        return CatequeseInfantilForm(data=data)

    # ------------------------------------------------
    # Turma dentro da faixa de nascimento configurada
    # ------------------------------------------------
    def test_turma_dentro_da_faixa_valido(self):
        form = self.make_form(
            data_nascimento=datetime.date(2019, 5, 10),
            turma=self.turma_pre.id,
        )
        self.assertTrue(form.is_valid())

    def test_nascido_no_primeiro_dia_da_faixa_valido(self):
        form = self.make_form(
            data_nascimento=datetime.date(2018, 1, 1),
            turma=self.turma_pre.id,
        )
        self.assertTrue(form.is_valid())

    def test_nascido_no_ultimo_dia_da_faixa_valido(self):
        form = self.make_form(
            data_nascimento=datetime.date(2020, 12, 31),
            turma=self.turma_pre.id,
        )
        self.assertTrue(form.is_valid())

    def test_nascido_depois_da_idade_minima_invalido(self):
        """Criança mais nova do que a turma aceita."""
        form = self.make_form(
            data_nascimento=datetime.date(2018, 1, 1),
            turma=self.turma_1a_etapa.id,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("nascidos até 31/12/2017", form.errors.get("turma")[0])

    def test_nascido_antes_da_idade_maxima_invalido(self):
        """Criança mais velha do que a turma aceita."""
        form = self.make_form(
            data_nascimento=datetime.date(2017, 12, 31),
            turma=self.turma_pre.id,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("nascidos a partir de 01/01/2018", form.errors.get("turma")[0])

    def test_turma_so_com_idade_maxima(self):
        turma = TurmaCatequeseInfantil.objects.create(nome="Só data inicial", idade_maxima=datetime.date(2015, 1, 1))
        self.assertTrue(self.make_form(data_nascimento=datetime.date(2022, 1, 1), turma=turma.id).is_valid())
        self.assertFalse(self.make_form(data_nascimento=datetime.date(2014, 12, 31), turma=turma.id).is_valid())

    def test_turma_so_com_idade_minima(self):
        turma = TurmaCatequeseInfantil.objects.create(nome="Só data final", idade_minima=datetime.date(2017, 12, 31))
        self.assertTrue(self.make_form(data_nascimento=datetime.date(2010, 1, 1), turma=turma.id).is_valid())
        self.assertFalse(self.make_form(data_nascimento=datetime.date(2018, 1, 1), turma=turma.id).is_valid())

    def test_turma_sem_restricao_aceita_qualquer_idade(self):
        form = self.make_form(
            data_nascimento=datetime.date(2010, 1, 1),
            turma=self.turma_sem_restricao.id,
        )
        self.assertTrue(form.is_valid())

    # ------------------------------------------------
    # Obrigatoriedade e turmas inativas
    # ------------------------------------------------
    def test_turma_obrigatoria(self):
        form = self.make_form(turma='')
        self.assertFalse(form.is_valid())
        self.assertIn("turma", form.errors)

    def test_turma_inativa_nao_aparece_no_queryset_do_form(self):
        form = CatequeseInfantilForm()
        ids_disponiveis = list(form.fields['turma'].queryset.values_list('id', flat=True))
        self.assertNotIn(self.turma_inativa.id, ids_disponiveis)

    def test_turma_inativa_nao_pode_ser_selecionada(self):
        form = self.make_form(
            data_nascimento=datetime.date(2016, 1, 1),
            turma=self.turma_inativa.id,
        )
        self.assertFalse(form.is_valid())


class CatequeseInfantilFormLimiteVagasTests(TestCase):

    def setUp(self):
        self.turma = TurmaCatequeseInfantil.objects.create(
            nome="1a Etapa - Quarta às 19:30h", vagas_maximas=20,
            idade_maxima=datetime.date(2015, 1, 1), idade_minima=datetime.date(2017, 12, 31),
        )
        self.base_data = {
            'nome': 'Maria Silva',
            'sexo': 'F',
            'data_nascimento': datetime.date(2016, 5, 10),  # dentro da faixa da turma
            'naturalidade': 'São Paulo',

            'nome_pai': 'João da Silva',
            'nome_mae': 'Ana da Silva',

            'endereco': 'Rua teste',
            'cidade': 'SP',
            'uf': 'SP',

            'celular_pai': '1199999',
            'celular_mae': '1199999',

            'batizado': False,

            'turma': self.turma.id,

            'possui_deficiencia': False,
            'possui_transtorno': False,
            'medicamento_uso_continuo': False,
            'acompanhamento_psicologico': False,

            'nome_responsavel': 'Maria Souza',
            'cpf_responsavel': '00011122233',
            'endereco_responsavel': 'Rua teste'
        }

    # helper
    def make_form(self, **kwargs):
        data = self.base_data.copy()
        data.update(kwargs)
        return CatequeseInfantilForm(data=data)

    def test_limite_de_vagas_valido_quando_ha_espaco(self):
        """
        Deve aceitar cadastro quando ainda houver menos inscritos do que
        turma.vagas_maximas.
        """
        for i in range(19):
            CatequeseInfantilModel.objects.create(
                nome=f"Crianca {i}",
                sexo='F',
                data_nascimento=datetime.date(2019, 1, 1),
                naturalidade='SP',
                turma=self.turma,
                nome_responsavel="Responsável Teste", cpf_responsavel="123.456.789-00",
                endereco="Rua teste", cidade="SP", uf="SP", endereco_responsavel="Rua teste",
            )

        form = self.make_form(nome='Nova Criança')
        self.assertTrue(form.is_valid())

    def test_limite_de_vagas_invalido_quando_turma_lotada(self):
        """
        Deve impedir o cadastro quando a turma já atingiu vagas_maximas.
        """
        for i in range(20):
            CatequeseInfantilModel.objects.create(
                nome=f"Crianca {i}",
                sexo='F',
                data_nascimento=datetime.date(2018, 1, 1),
                naturalidade='SP',
                turma=self.turma,
                nome_responsavel="Responsável Teste", cpf_responsavel="123.456.789-00",
                endereco="Rua teste", cidade="SP", uf="SP", endereco_responsavel="Rua teste",
            )

        form = self.make_form(nome='Crianca Excedente')
        self.assertFalse(form.is_valid())
        self.assertIn("lotada", form.errors.get("turma")[0])

    def test_sem_limite_de_vagas_aceita_qualquer_quantidade(self):
        turma_livre = TurmaCatequeseInfantil.objects.create(nome="Transferência")
        for i in range(30):
            CatequeseInfantilModel.objects.create(
                nome=f"Crianca {i}",
                sexo='F',
                data_nascimento=datetime.date(2010, 1, 1),
                naturalidade='SP',
                turma=turma_livre,
                nome_responsavel="Responsável Teste", cpf_responsavel="123.456.789-00",
                endereco="Rua teste", cidade="SP", uf="SP", endereco_responsavel="Rua teste",
            )

        form = self.make_form(nome='Mais uma criança', turma=turma_livre.id)
        self.assertTrue(form.is_valid())
