from django.test import TestCase
from core.forms import TurmaForm


class TurmaFormTest(TestCase):

    def make_form(self, **kwargs):
        data = {
            'nome': '1a Etapa - Quarta às 19:30h',
            'ativa': True,
            'vagas_maximas': 20,
            'idade_minima': 9,
            'idade_maxima': 11,
            'ordem': 1,
        }
        data.update(kwargs)
        return TurmaForm(data=data)

    def test_form_valido(self):
        form = self.make_form()
        self.assertTrue(form.is_valid())

    def test_sem_limite_de_vagas_e_idade_e_valido(self):
        form = self.make_form(vagas_maximas='', idade_minima='', idade_maxima='')
        self.assertTrue(form.is_valid())

    def test_idade_maxima_menor_que_minima_invalido(self):
        form = self.make_form(idade_minima=12, idade_maxima=8)
        self.assertFalse(form.is_valid())
        self.assertIn('idade_maxima', form.errors)

    def test_nome_obrigatorio(self):
        form = self.make_form(nome='')
        self.assertFalse(form.is_valid())
        self.assertIn('nome', form.errors)
