from django.test import TestCase
from core.forms import TurmaForm


class TurmaFormTest(TestCase):

    def make_form(self, **kwargs):
        data = {
            'nome': '1a Etapa - Quarta às 19:30h',
            'ativa': True,
            'vagas_maximas': 20,
            'idade_maxima': '2015-01-01',  # nascidos a partir de
            'idade_minima': '2017-12-31',  # nascidos até
            'ordem': 1,
        }
        data.update(kwargs)
        return TurmaForm(data=data)

    def test_form_valido(self):
        form = self.make_form()
        self.assertTrue(form.is_valid())

    def test_datas_sao_convertidas_para_date(self):
        form = self.make_form()
        form.is_valid()
        self.assertEqual(str(form.cleaned_data['idade_maxima']), '2015-01-01')
        self.assertEqual(str(form.cleaned_data['idade_minima']), '2017-12-31')

    def test_sem_limite_de_vagas_e_idade_e_valido(self):
        form = self.make_form(vagas_maximas='', idade_minima='', idade_maxima='')
        self.assertTrue(form.is_valid())

    def test_somente_uma_das_datas_e_valido(self):
        form = self.make_form(idade_minima='')
        self.assertTrue(form.is_valid())

    def test_mesma_data_nas_duas_e_valido(self):
        form = self.make_form(idade_maxima='2016-06-01', idade_minima='2016-06-01')
        self.assertTrue(form.is_valid())

    def test_nascidos_ate_anterior_a_nascidos_a_partir_de_invalido(self):
        form = self.make_form(idade_maxima='2022-12-31', idade_minima='2015-01-01')
        self.assertFalse(form.is_valid())
        self.assertIn('idade_minima', form.errors)

    def test_data_invalida(self):
        form = self.make_form(idade_maxima='2015-13-45')
        self.assertFalse(form.is_valid())
        self.assertIn('idade_maxima', form.errors)

    def test_widget_de_data(self):
        form = TurmaForm()
        for campo in ('idade_minima', 'idade_maxima'):
            with self.subTest(campo):
                self.assertEqual(form.fields[campo].widget.input_type, 'date')

    def test_nome_obrigatorio(self):
        form = self.make_form(nome='')
        self.assertFalse(form.is_valid())
        self.assertIn('nome', form.errors)
