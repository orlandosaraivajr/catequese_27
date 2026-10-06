import datetime
from django.test import TestCase
from core.models import Perseveranca_MEJ_Model, TurmaPerseveranca_MEJ
from core.forms import PerseverancaMejForm


class PerseverancaMejFormTurmaTests(TestCase):

    def setUp(self):
        # Perseverança: nascidos entre 01/01/2011 e 31/12/2014
        self.turma_com_faixa = TurmaPerseveranca_MEJ.objects.create(
            nome="Perseverança e MEJ - 11 a 14 anos - Quinta às 19:30h",
            idade_maxima=datetime.date(2011, 1, 1), idade_minima=datetime.date(2014, 12, 31),
        )
        self.turma_sem_restricao = TurmaPerseveranca_MEJ.objects.create(nome="MEJ - Terça às 19:30h")
        self.turma_inativa = TurmaPerseveranca_MEJ.objects.create(nome="Turma Encerrada", ativa=False)

        self.valid_base_data = {
            'nome': 'Maria Silva',
            'sexo': 'F',
            'data_nascimento': datetime.date(2013, 5, 10),
            'naturalidade': 'São Paulo',

            'nome_pai': 'João da Silva',
            'nome_mae': 'Ana da Silva',

            'endereco': 'Rua teste',
            'cidade': 'Rio Claro',
            'uf': 'SP',

            'celular_pai': '1199999',
            'celular_mae': '1199999',

            'batizado': False,
            'primeira_eucaristia': False,

            'turma': self.turma_com_faixa.id,

            'possui_deficiencia': False,
            'possui_transtorno': False,
            'medicamento_uso_continuo': False,
            'acompanhamento_psicologico': False,

            'nome_responsavel': 'Maria Souza',
            'cpf_responsavel': '00011122233',
            'endereco_responsavel': 'Rua teste',
        }

    def make_form(self, **kwargs):
        data = self.valid_base_data.copy()
        data.update(kwargs)
        return PerseverancaMejForm(data=data)

    # ------------------------------------
    # Faixa de nascimento
    # ------------------------------------
    def test_turma_dentro_da_faixa_valido(self):
        form = self.make_form()
        self.assertTrue(form.is_valid(), form.errors)

    def test_limites_da_faixa_sao_inclusivos(self):
        self.assertTrue(self.make_form(data_nascimento=datetime.date(2011, 1, 1)).is_valid())
        self.assertTrue(self.make_form(data_nascimento=datetime.date(2014, 12, 31)).is_valid())

    def test_mais_novo_que_a_turma_invalido(self):
        form = self.make_form(data_nascimento=datetime.date(2015, 1, 1))
        self.assertFalse(form.is_valid())
        self.assertIn("nascidos até 31/12/2014", form.errors.get("turma")[0])

    def test_mais_velho_que_a_turma_invalido(self):
        form = self.make_form(data_nascimento=datetime.date(2010, 12, 31))
        self.assertFalse(form.is_valid())
        self.assertIn("nascidos a partir de 01/01/2011", form.errors.get("turma")[0])

    def test_turma_sem_restricao_aceita_qualquer_idade(self):
        form = self.make_form(
            data_nascimento=datetime.date(2000, 1, 1),
            turma=self.turma_sem_restricao.id,
        )
        self.assertTrue(form.is_valid(), form.errors)

    # ------------------------------------
    # Obrigatoriedade e turmas inativas
    # ------------------------------------
    def test_turma_obrigatoria(self):
        form = self.make_form(turma='')
        self.assertFalse(form.is_valid())
        self.assertIn("turma", form.errors)

    def test_label_do_campo_turma(self):
        self.assertEqual(PerseverancaMejForm().fields['turma'].label, 'Horário do MEJ:')

    def test_turma_inativa_nao_aparece_no_queryset_do_form(self):
        form = PerseverancaMejForm()
        ids_disponiveis = list(form.fields['turma'].queryset.values_list('id', flat=True))
        self.assertNotIn(self.turma_inativa.id, ids_disponiveis)
        self.assertIn(self.turma_com_faixa.id, ids_disponiveis)

    def test_turma_inativa_nao_pode_ser_selecionada(self):
        form = self.make_form(turma=self.turma_inativa.id)
        self.assertFalse(form.is_valid())
        self.assertIn("turma", form.errors)

    def test_edicao_mantem_turma_inativa_atual_selecionavel(self):
        ficha = self._criar_ficha(self.turma_inativa)
        form = PerseverancaMejForm(instance=ficha)
        ids_disponiveis = list(form.fields['turma'].queryset.values_list('id', flat=True))
        self.assertIn(self.turma_inativa.id, ids_disponiveis)

    # ------------------------------------
    # Limite de vagas
    # ------------------------------------
    def _criar_ficha(self, turma, nome="Jovem Teste"):
        return Perseveranca_MEJ_Model.objects.create(
            nome=nome, sexo="M", data_nascimento=datetime.date(2013, 1, 1),
            endereco="Rua X", cidade="Rio Claro", uf="SP", turma=turma,
            nome_responsavel="Responsável Teste", cpf_responsavel="123.456.789-00",
            endereco_responsavel="Rua X",
        )

    def _inscrever(self, turma, quantidade):
        for i in range(quantidade):
            self._criar_ficha(turma, nome=f"Jovem {i}")

    def test_limite_de_vagas_valido_quando_ha_vaga(self):
        self.turma_com_faixa.vagas_maximas = 2
        self.turma_com_faixa.save()
        self._inscrever(self.turma_com_faixa, 1)
        self.assertTrue(self.make_form().is_valid())

    def test_limite_de_vagas_invalido_quando_turma_lotada(self):
        self.turma_com_faixa.vagas_maximas = 2
        self.turma_com_faixa.save()
        self._inscrever(self.turma_com_faixa, 2)
        form = self.make_form()
        self.assertFalse(form.is_valid())
        self.assertIn("lotada", form.errors.get("turma")[0])

    def test_sem_limite_de_vagas_aceita_sempre(self):
        self._inscrever(self.turma_sem_restricao, 5)
        self.assertTrue(self.make_form(turma=self.turma_sem_restricao.id).is_valid())
