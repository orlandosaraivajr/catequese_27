from django.test import TestCase, Client
from django.shortcuts import resolve_url as r
from http import HTTPStatus
from core.models import CatequeseInfantilModel, TurmaCatequeseInfantil, SementinhaModel, TurmaSementinha
from datetime import date
from core.test.acessos import GRUPO_SECRETARIA, logar


class ListarFichasGetTest(TestCase):
    def setUp(self):
        self.client = Client()
        logar(self.client, 'secretaria', GRUPO_SECRETARIA)
        self.url = r('core:listar_fichas')

    def test_status_code(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, HTTPStatus.OK)

    def test_template_used(self):
        resp = self.client.get(self.url)
        self.assertTemplateUsed(resp, 'listar_fichas.html')

    def test_context_contains_mensagem(self):
        resp = self.client.get(self.url)
        self.assertIn('mensagem', resp.context)
        self.assertEqual(resp.context['mensagem'], 'Fichas Pendentes de Impressão')


# ---------------------------
#   TESTES DE LISTAGEM
# ---------------------------

class ListarFichasSemRegistrosTest(TestCase):
    def setUp(self):
        self.client = Client()
        logar(self.client, 'secretaria', GRUPO_SECRETARIA)
        self.url = r('core:listar_fichas')
        self.resp = self.client.get(self.url)

    def test_lista_vazia(self):
        fichas = self.resp.context['fichas']
        self.assertEqual(list(fichas), [])  # deve estar vazio


class ListarFichasUmRegistroTest(TestCase):
    def setUp(self):
        self.client = Client()
        logar(self.client, 'secretaria', GRUPO_SECRETARIA)
        self.url = r('core:listar_fichas')
        self.turma = TurmaCatequeseInfantil.objects.create(nome="1a Etapa - Quarta às 19:30h", idade_maxima=date(2015, 1, 1), idade_minima=date(2017, 12, 31))

        # Ficha pendente de impressão
        self.f1 = CatequeseInfantilModel.objects.create(
            nome='Ana',
            sexo='F',
            data_nascimento=date(2015, 6, 1),
            endereco='Rua das Flores, 123',
            cidade='Araras',
            uf='SP',
            turma=self.turma,
            nome_responsavel='Maria da Silva',
            cpf_responsavel='123.456.789-00',
            endereco_responsavel='Rua das Flores, 123',
            ficha_impressa=False,
        )

        self.resp = self.client.get(self.url)

    def test_lista_com_um_registro(self):
        fichas = list(self.resp.context['fichas'])
        self.assertEqual(len(fichas), 1)
        self.assertIn(self.f1, fichas)


class ListarFichasDoisRegistrosTest(TestCase):
    def setUp(self):
        self.client = Client()
        logar(self.client, 'secretaria', GRUPO_SECRETARIA)
        self.url = r('core:listar_fichas')
        self.turma = TurmaCatequeseInfantil.objects.create(nome="1a Etapa - Quarta às 19:30h", idade_maxima=date(2015, 1, 1), idade_minima=date(2017, 12, 31))

        # Ficha pendente (deve aparecer)
        self.f1 = CatequeseInfantilModel.objects.create(
            nome='Ana',
            sexo='F',
            data_nascimento=date(2015, 6, 1),
            endereco='Rua das Flores, 123',
            cidade='Araras',
            uf='SP',
            turma=self.turma,
            nome_responsavel='Maria da Silva',
            cpf_responsavel='123.456.789-00',
            endereco_responsavel='Rua das Flores, 123',
            ficha_impressa=False,
        )

        # Ficha já impressa (NÃO deve aparecer)
        self.f2 = CatequeseInfantilModel.objects.create(
            nome='Carlos',
            sexo='M',
            data_nascimento=date(2015, 6, 1),
            endereco='Rua das Flores, 123',
            cidade='Araras',
            uf='SP',
            turma=self.turma,
            nome_responsavel='Maria da Silva',
            cpf_responsavel='123.456.789-00',
            endereco_responsavel='Rua das Flores, 123',
            ficha_impressa=True,
        )

        self.resp = self.client.get(self.url)

    def test_somente_nao_impressas_listadas(self):
        fichas = list(self.resp.context['fichas'])

        self.assertIn(self.f1, fichas)   # deve estar
        self.assertNotIn(self.f2, fichas)  # não deve estar

    def test_quantidade_uma_ficha(self):
        fichas = list(self.resp.context['fichas'])
        self.assertEqual(len(fichas), 1)


class ListarFichasSementinhaTest(TestCase):
    """A secretaria vê as fichas da Sementinha em uma tabela própria."""

    def setUp(self):
        logar(self.client, 'secretaria', GRUPO_SECRETARIA)
        turma = TurmaSementinha.objects.create(nome="Sementinha - Sábado às 9:00h")
        dados = dict(sexo='F', data_nascimento=date(2021, 6, 1), endereco='Rua X', cidade='Araras',
                     uf='SP', turma=turma, nome_responsavel='Maria da Silva',
                     cpf_responsavel='123.456.789-00', endereco_responsavel='Rua X')
        self.pendente = SementinhaModel.objects.create(nome='Ana Pendente', **dados)
        self.impressa = SementinhaModel.objects.create(nome='Bia Impressa', ficha_impressa=True, **dados)
        self.assinada = SementinhaModel.objects.create(nome='Caio Assinado', ficha_impressa=True,
                                                       ficha_assinada=True, **dados)

    def test_pendentes_lista_so_nao_impressas(self):
        resp = self.client.get(r('core:listar_fichas'))
        self.assertEqual(list(resp.context['fichasSementinha']), [self.pendente])

    def test_todas_lista_nao_assinadas(self):
        resp = self.client.get(r('core:listar_todas_fichas'))
        self.assertEqual(list(resp.context['fichasSementinha']), [self.pendente, self.impressa])

    def test_ficha_pendente_tem_acao_de_imprimir(self):
        resp = self.client.get(r('core:listar_fichas'))
        self.assertContains(resp, 'Sementinha')
        self.assertContains(resp, r('core:imprimir_ficha_sementinha'))

    def test_ficha_impressa_tem_acoes_de_assinar_e_remover(self):
        resp = self.client.get(r('core:listar_todas_fichas'))
        self.assertContains(resp, r('core:assinar_ficha_sementinha'))
        self.assertContains(resp, r('core:remover_ficha_sementinha'))

    def test_fichas_da_sementinha_nao_aparecem_na_catequese(self):
        resp = self.client.get(r('core:listar_fichas'))
        self.assertEqual(list(resp.context['fichas']), [])
