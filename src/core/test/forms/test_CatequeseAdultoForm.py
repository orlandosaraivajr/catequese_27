import datetime
from django.test import TestCase
from core.models import CatequeseAdultoModel, TurmaCatequeseAdulto
from core.forms import CatequeseAdultoForm


class CatequeseAdultoFormTurmaTests(TestCase):

    def setUp(self):
        # Nascidos entre 01/01/1980 e 31/12/1999
        self.turma_com_faixa = TurmaCatequeseAdulto.objects.create(
            nome="Quinta às 19:30h - SEM Batismo",
            idade_maxima=datetime.date(1980, 1, 1), idade_minima=datetime.date(1999, 12, 31),
        )
        self.turma_sem_restricao = TurmaCatequeseAdulto.objects.create(nome="Sábado às 09h - SEM Batismo")
        self.turma_inativa = TurmaCatequeseAdulto.objects.create(nome="Turma Encerrada", ativa=False)

        self.valid_base_data = {
            'nome': 'Maria Silva',
            'cpf': '000.111.222-33',
            'sexo': 'F',
            'celular': '19999990000',
            'data_nascimento': datetime.date(1990, 5, 10),
            'naturalidade': 'São Paulo',

            'nome_pai': 'João da Silva',
            'nome_mae': 'Ana da Silva',

            'endereco': 'Rua teste',
            'cidade': 'Rio Claro',
            'uf': 'SP',
            'estado_civil': 'Solteira',

            'batizado': False,
            'primeira_eucaristia': False,
            'casado_igreja': False,

            'turma': self.turma_com_faixa.id,
        }

    def make_form(self, **kwargs):
        data = self.valid_base_data.copy()
        data.update(kwargs)
        return CatequeseAdultoForm(data=data)

    # ------------------------------------
    # Faixa de nascimento
    # ------------------------------------
    def test_turma_dentro_da_faixa_valido(self):
        form = self.make_form()
        self.assertTrue(form.is_valid(), form.errors)

    def test_limites_da_faixa_sao_inclusivos(self):
        self.assertTrue(self.make_form(data_nascimento=datetime.date(1980, 1, 1)).is_valid())
        self.assertTrue(self.make_form(data_nascimento=datetime.date(1999, 12, 31)).is_valid())

    def test_mais_novo_que_a_turma_invalido(self):
        form = self.make_form(data_nascimento=datetime.date(2000, 1, 1))
        self.assertFalse(form.is_valid())
        self.assertIn("nascidos até 31/12/1999", form.errors.get("turma")[0])

    def test_mais_velho_que_a_turma_invalido(self):
        form = self.make_form(data_nascimento=datetime.date(1979, 12, 31))
        self.assertFalse(form.is_valid())
        self.assertIn("nascidos a partir de 01/01/1980", form.errors.get("turma")[0])

    def test_turma_sem_restricao_aceita_qualquer_idade(self):
        form = self.make_form(
            data_nascimento=datetime.date(1950, 1, 1),
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
        self.assertEqual(CatequeseAdultoForm().fields['turma'].label, 'Horário da Catequese:')

    def test_turma_inativa_nao_aparece_no_queryset_do_form(self):
        form = CatequeseAdultoForm()
        ids_disponiveis = list(form.fields['turma'].queryset.values_list('id', flat=True))
        self.assertNotIn(self.turma_inativa.id, ids_disponiveis)
        self.assertIn(self.turma_com_faixa.id, ids_disponiveis)

    def test_turma_inativa_nao_pode_ser_selecionada(self):
        form = self.make_form(turma=self.turma_inativa.id)
        self.assertFalse(form.is_valid())
        self.assertIn("turma", form.errors)

    def test_edicao_mantem_turma_inativa_atual_selecionavel(self):
        ficha = CatequeseAdultoModel.objects.create(
            nome="Maria Silva", sexo="F", data_nascimento=datetime.date(1990, 5, 10),
            endereco="Rua X", cidade="Rio Claro", uf="SP", estado_civil="Solteira",
            turma=self.turma_inativa,
        )
        form = CatequeseAdultoForm(instance=ficha)
        ids_disponiveis = list(form.fields['turma'].queryset.values_list('id', flat=True))
        self.assertIn(self.turma_inativa.id, ids_disponiveis)

    # ------------------------------------
    # Limite de vagas
    # ------------------------------------
    def _inscrever(self, turma, quantidade):
        for i in range(quantidade):
            CatequeseAdultoModel.objects.create(
                nome=f"Catequizando {i}", sexo="M", data_nascimento=datetime.date(1990, 1, 1),
                endereco="Rua X", cidade="Rio Claro", uf="SP", estado_civil="Solteiro",
                turma=turma,
            )

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
