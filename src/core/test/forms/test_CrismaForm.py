import datetime
from django.test import TestCase
from core.models import CrismaModel, TurmaCrisma
from core.forms import CrismaForm


def ano_relativo(anos_atras):
    """Ano de nascimento que resulta na idade projetada informada (ano seguinte - ano)."""
    return datetime.date.today().year + 1 - anos_atras


class CrismaFormTurmaTests(TestCase):

    def setUp(self):
        # Nascidos com idade projetada entre 15 e 17 anos
        self.inicio = datetime.date(ano_relativo(17), 1, 1)
        self.fim = datetime.date(ano_relativo(15), 12, 31)
        self.turma_com_faixa = TurmaCrisma.objects.create(
            nome="Quinta às 19:30h", idade_maxima=self.inicio, idade_minima=self.fim,
        )
        self.turma_sem_restricao = TurmaCrisma.objects.create(nome="Sábado às 09h")
        self.turma_inativa = TurmaCrisma.objects.create(nome="Turma Encerrada", ativa=False)

        self.valid_base_data = {
            'nome': 'Maria Silva',
            'sexo': 'F',
            'data_nascimento': datetime.date(ano_relativo(16), 5, 10),
            'naturalidade': 'São Paulo',

            'nome_pai': 'João da Silva',
            'nome_mae': 'Ana da Silva',

            'endereco': 'Rua teste',
            'cidade': 'SP',
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
        return CrismaForm(data=data)

    # ------------------------------------
    # Faixa de nascimento
    # ------------------------------------
    def test_turma_dentro_da_faixa_valido(self):
        form = self.make_form()
        self.assertTrue(form.is_valid(), form.errors)

    def test_limites_da_faixa_sao_inclusivos(self):
        self.assertTrue(self.make_form(data_nascimento=self.inicio).is_valid())
        self.assertTrue(self.make_form(data_nascimento=self.fim).is_valid())

    def test_mais_novo_que_a_turma_invalido(self):
        form = self.make_form(data_nascimento=datetime.date(ano_relativo(14), 1, 1))
        self.assertFalse(form.is_valid())
        self.assertIn(f"nascidos até {self.fim:%d/%m/%Y}", form.errors.get("turma")[0])

    def test_mais_velho_que_a_turma_invalido(self):
        form = self.make_form(data_nascimento=datetime.date(ano_relativo(18), 12, 31))
        self.assertFalse(form.is_valid())
        self.assertIn(f"nascidos a partir de {self.inicio:%d/%m/%Y}", form.errors.get("turma")[0])

    def test_turma_sem_restricao_aceita_qualquer_idade_permitida(self):
        form = self.make_form(
            data_nascimento=datetime.date(ano_relativo(19), 1, 1),
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

    def test_turma_inativa_nao_aparece_no_queryset_do_form(self):
        form = CrismaForm()
        ids_disponiveis = list(form.fields['turma'].queryset.values_list('id', flat=True))
        self.assertNotIn(self.turma_inativa.id, ids_disponiveis)
        self.assertIn(self.turma_com_faixa.id, ids_disponiveis)

    def test_turma_inativa_nao_pode_ser_selecionada(self):
        form = self.make_form(turma=self.turma_inativa.id)
        self.assertFalse(form.is_valid())
        self.assertIn("turma", form.errors)

    def test_edicao_mantem_turma_inativa_atual_selecionavel(self):
        ficha = CrismaModel.objects.create(
            nome="Maria Silva", sexo="F", data_nascimento=self.valid_base_data['data_nascimento'],
            endereco="Rua X", cidade="SP", uf="SP", turma=self.turma_inativa,
        )
        form = CrismaForm(instance=ficha)
        ids_disponiveis = list(form.fields['turma'].queryset.values_list('id', flat=True))
        self.assertIn(self.turma_inativa.id, ids_disponiveis)

    # ------------------------------------
    # Limite de vagas
    # ------------------------------------
    def _inscrever(self, turma, quantidade):
        for i in range(quantidade):
            CrismaModel.objects.create(
                nome=f"Crismando {i}", sexo="M", data_nascimento=self.valid_base_data['data_nascimento'],
                endereco="Rua X", cidade="SP", uf="SP", turma=turma,
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
