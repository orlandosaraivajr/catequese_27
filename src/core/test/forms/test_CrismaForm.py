import datetime
from unittest import mock
from django.test import TestCase
from core.models import CrismaModel, TurmaCrisma
from core.forms import CrismaForm


def ano_relativo(anos_atras):
    """Ano de nascimento que resulta na idade projetada informada (ano seguinte - ano)."""
    return datetime.date.today().year + 1 - anos_atras


# ------------------------------------------------------------------
# Regras vigentes de CrismaForm.clean_data_nascimento.
# Se algum teste abaixo falhar, a regra do formulário mudou: confirme se
# a mudança foi intencional e atualize estas constantes.
# ------------------------------------------------------------------
IDADE_MINIMA = 11
IDADE_MAXIMA = 20
MSG_OBRIGATORIA = "Informe a data de nascimento."
MSG_IDADE_MINIMA = "Necessário 11 anos para pré-matrícula na Crisma."
MSG_IDADE_MAXIMA = "Acima de 20 anos, inscrever-se na Catequese de Adulto."


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


class CrismaFormDataNascimentoTests(TestCase):
    """
    Testes de regressão de clean_data_nascimento.

    Usam uma turma sem faixa de nascimento para isolar a regra de idade
    da validação de turma. Cada teste fixa um aspecto da regra atual
    (limites, mensagens, forma de cálculo) e falha se ele mudar.
    """

    def setUp(self):
        self.turma = TurmaCrisma.objects.create(nome="Sábado às 09h")
        self.base = {
            'nome': 'Maria Silva', 'sexo': 'F', 'naturalidade': 'São Paulo',
            'nome_pai': 'João da Silva', 'nome_mae': 'Ana da Silva',
            'endereco': 'Rua teste', 'cidade': 'SP', 'uf': 'SP',
            'celular_pai': '1199999', 'celular_mae': '1199999',
            'batizado': False, 'primeira_eucaristia': False,
            'turma': self.turma.id,
            'possui_deficiencia': False, 'possui_transtorno': False,
            'medicamento_uso_continuo': False, 'acompanhamento_psicologico': False,
            'nome_responsavel': 'Maria Souza', 'cpf_responsavel': '00011122233',
            'endereco_responsavel': 'Rua teste',
        }

    def form_com_idade(self, idade, mes=6, dia=15):
        data = dict(self.base, data_nascimento=datetime.date(ano_relativo(idade), mes, dia))
        return CrismaForm(data=data)

    def erros_data(self, form):
        form.is_valid()
        return form.errors.get('data_nascimento', [])

    # ------------------------------------
    # Obrigatoriedade
    # ------------------------------------
    def test_data_ausente_exibe_mensagem_de_obrigatoria(self):
        form = CrismaForm(data=dict(self.base, data_nascimento=''))
        self.assertEqual(self.erros_data(form), [MSG_OBRIGATORIA])

    # ------------------------------------
    # Limite mínimo
    # ------------------------------------
    def test_idade_minima_vigente_e_11(self):
        self.assertEqual(self.erros_data(self.form_com_idade(IDADE_MINIMA)), [],
                         f"{IDADE_MINIMA} anos deveria ser aceito: o limite mínimo foi elevado?")

    def test_um_ano_abaixo_do_minimo_e_recusado(self):
        self.assertEqual(self.erros_data(self.form_com_idade(IDADE_MINIMA - 1)), [MSG_IDADE_MINIMA],
                         f"{IDADE_MINIMA - 1} anos deveria ser recusado: o limite mínimo foi reduzido?")

    def test_limite_antigo_de_15_anos_nao_e_mais_exigido(self):
        for idade in range(IDADE_MINIMA, 15):
            with self.subTest(idade=idade):
                self.assertEqual(self.erros_data(self.form_com_idade(idade)), [])

    def test_mensagem_minima_cita_a_idade_minima(self):
        self.assertIn(f"{IDADE_MINIMA} anos", MSG_IDADE_MINIMA)
        self.assertEqual(self.erros_data(self.form_com_idade(IDADE_MINIMA - 1)), [MSG_IDADE_MINIMA])

    # ------------------------------------
    # Limite máximo
    # ------------------------------------
    def test_idade_maxima_vigente_e_20(self):
        self.assertEqual(self.erros_data(self.form_com_idade(IDADE_MAXIMA)), [],
                         f"{IDADE_MAXIMA} anos deveria ser aceito: o limite máximo foi reduzido?")

    def test_um_ano_acima_do_maximo_e_recusado(self):
        self.assertEqual(self.erros_data(self.form_com_idade(IDADE_MAXIMA + 1)), [MSG_IDADE_MAXIMA],
                         f"{IDADE_MAXIMA + 1} anos deveria ser recusado: o limite máximo foi elevado?")

    # ------------------------------------
    # Faixa completa
    # ------------------------------------
    def test_toda_a_faixa_permitida_e_aceita(self):
        for idade in range(IDADE_MINIMA, IDADE_MAXIMA + 1):
            with self.subTest(idade=idade):
                self.assertEqual(self.erros_data(self.form_com_idade(idade)), [])

    def test_idades_fora_da_faixa_sao_recusadas_com_a_mensagem_certa(self):
        casos = [(idade, MSG_IDADE_MINIMA) for idade in range(1, IDADE_MINIMA)]
        casos += [(idade, MSG_IDADE_MAXIMA) for idade in range(IDADE_MAXIMA + 1, IDADE_MAXIMA + 15)]
        for idade, mensagem in casos:
            with self.subTest(idade=idade):
                self.assertEqual(self.erros_data(self.form_com_idade(idade)), [mensagem])

    # ------------------------------------
    # Forma de cálculo
    # ------------------------------------
    def test_calculo_considera_apenas_o_ano_de_nascimento(self):
        """1º/jan e 31/dez do mesmo ano têm o mesmo resultado (mês e dia são ignorados)."""
        for idade in (IDADE_MINIMA - 1, IDADE_MINIMA, IDADE_MAXIMA, IDADE_MAXIMA + 1):
            with self.subTest(idade=idade):
                self.assertEqual(
                    self.erros_data(self.form_com_idade(idade, 1, 1)),
                    self.erros_data(self.form_com_idade(idade, 12, 31)),
                )

    def test_idade_e_projetada_para_o_ano_seguinte(self):
        """Com 'hoje' fixado em 14/11/2026, a referência é 2027."""

        class DataFixa(datetime.date):
            @classmethod
            def today(cls):
                return cls(2026, 11, 14)

        casos = [
            (2016, []),                  # 2027 - 2016 = 11 -> aceito
            (2017, [MSG_IDADE_MINIMA]),  # 10 -> recusado
            (2007, []),                  # 20 -> aceito
            (2006, [MSG_IDADE_MAXIMA]),  # 21 -> recusado
        ]
        with mock.patch('core.forms.date', DataFixa):
            for ano, esperado in casos:
                with self.subTest(ano=ano):
                    form = CrismaForm(data=dict(self.base, data_nascimento=datetime.date(ano, 6, 15)))
                    self.assertEqual(self.erros_data(form), esperado)

    def test_data_valida_e_retornada_sem_alteracao(self):
        nascimento = datetime.date(ano_relativo(16), 5, 10)
        form = CrismaForm(data=dict(self.base, data_nascimento=nascimento))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['data_nascimento'], nascimento)
