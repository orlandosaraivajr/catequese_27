from datetime import date
from http import HTTPStatus

from django.shortcuts import resolve_url as r
from django.test import TestCase

from core import models as m
from core.test.acessos import GRUPO_COORDENACAO, GRUPO_SECRETARIA, logar


def criar_crisma(**extra):
    dados = dict(nome='Ana Souza', sexo='F', data_nascimento=date(2021, 6, 1), endereco='Rua X',
                 cidade='Rio Claro', uf='SP', turma=m.TurmaCrisma.objects.create(nome='Quinta às 19:30h'))
    dados.update(extra)
    return m.CrismaModel.objects.create(**dados)


class AjustePastoraisAcessoTest(TestCase):
    """Somente a coordenação faz ajuste entre pastorais."""

    def setUp(self):
        self.ficha = criar_crisma()
        self.turma = m.TurmaSementinha.objects.create(nome='Sementinha - Sábado')
        self.urls = (
            r('core:ajuste_pastorais'),
            r('core:transferir_ficha_pastoral', 'crisma', self.ficha.id),
            r('core:transferir_ficha_pastoral_destino', 'crisma', self.ficha.id, 'sementinha'),
        )
        self.dados = {'turma': self.turma.id, 'nome_responsavel': 'Maria Souza',
                      'cpf_responsavel': '1', 'endereco_responsavel': 'Rua X'}

    def test_caminho(self):
        self.assertEqual(r('core:ajuste_pastorais'), '/coordenacao/ajuste-pastorais')

    def test_visitante_vai_para_o_login(self):
        for url in self.urls:
            with self.subTest(url=url):
                resp = self.client.get(url)
                self.assertRedirects(resp, f"{r('core:coordenacao')}?next={url}", fetch_redirect_response=False)

    def test_secretaria_recebe_acesso_negado_e_nao_transfere(self):
        logar(self.client, 'secretaria', GRUPO_SECRETARIA)
        for url in self.urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, HTTPStatus.FORBIDDEN)
        resp = self.client.post(self.urls[2], self.dados)
        self.assertEqual(resp.status_code, HTTPStatus.FORBIDDEN)
        self.assertTrue(m.CrismaModel.objects.filter(pk=self.ficha.pk).exists())

    def test_coordenacao_acessa(self):
        logar(self.client, 'coordenacao', GRUPO_COORDENACAO)
        for url in self.urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, HTTPStatus.OK)


class AjustePastoraisListagemTest(TestCase):
    def setUp(self):
        logar(self.client, 'coordenacao', GRUPO_COORDENACAO)
        self.ana = criar_crisma()
        self.bia = criar_crisma(nome='Bia Lima')
        turma = m.TurmaSementinha.objects.create(nome='Sementinha - Sábado')
        self.caio = m.SementinhaModel.objects.create(
            nome='Caio Prado', sexo='M', data_nascimento=date(2021, 1, 1), endereco='Rua X',
            cidade='Rio Claro', uf='SP', turma=turma,
            nome_responsavel='Maria Prado', cpf_responsavel='1', endereco_responsavel='Rua X',
        )

    def test_padrao_lista_fichas_da_crisma(self):
        resp = self.client.get(r('core:ajuste_pastorais'))
        self.assertTemplateUsed(resp, 'ajuste_pastorais.html')
        self.assertEqual(list(resp.context['fichas']), [self.ana, self.bia])

    def test_escolhe_pastoral(self):
        resp = self.client.get(r('core:ajuste_pastorais'), {'pastoral': 'sementinha'})
        self.assertEqual(list(resp.context['fichas']), [self.caio])

    def test_pastoral_invalida_volta_para_crisma(self):
        resp = self.client.get(r('core:ajuste_pastorais'), {'pastoral': 'noivos'})
        self.assertEqual(resp.context['origem'], 'crisma')

    def test_busca_por_nome(self):
        resp = self.client.get(r('core:ajuste_pastorais'), {'pastoral': 'crisma', 'busca': 'bia'})
        self.assertEqual(list(resp.context['fichas']), [self.bia])

    def test_link_transferir(self):
        resp = self.client.get(r('core:ajuste_pastorais'))
        self.assertContains(resp, r('core:transferir_ficha_pastoral', 'crisma', self.ana.id))

    def test_abas_das_pastorais(self):
        resp = self.client.get(r('core:ajuste_pastorais'))
        for titulo in ('Catequese Infantil', 'Sementinha', 'Crisma', 'MEJ'):
            with self.subTest(titulo=titulo):
                self.assertContains(resp, titulo)


class TransferirFichaPastoralTest(TestCase):
    def setUp(self):
        logar(self.client, 'coordenacao', GRUPO_COORDENACAO)
        self.ficha = criar_crisma(primeira_eucaristia=True, padrinho_nome='Carlos Padrinho', ficha_impressa=True)
        self.turma = m.TurmaSementinha.objects.create(nome='Sementinha - Sábado')
        self.url = r('core:transferir_ficha_pastoral_destino', 'crisma', self.ficha.id, 'sementinha')
        self.dados = {'turma': self.turma.id, 'nome_responsavel': 'Maria Souza',
                      'cpf_responsavel': '123.456.789-00', 'endereco_responsavel': 'Rua X'}

    def test_escolha_do_destino_lista_as_outras_pastorais(self):
        resp = self.client.get(r('core:transferir_ficha_pastoral', 'crisma', self.ficha.id))
        self.assertEqual(set(resp.context['destinos']), {'catequese_infantil', 'sementinha', 'mej'})
        self.assertContains(resp, self.url)

    def test_formulario_mostra_dados_perdidos(self):
        resp = self.client.get(self.url)
        self.assertContains(resp, 'serão perdidos')
        self.assertContains(resp, 'Carlos Padrinho')

    def test_turmas_so_do_destino_incluindo_inativas(self):
        inativa = m.TurmaSementinha.objects.create(nome='Antiga', ativa=False)
        m.TurmaCatequeseInfantil.objects.create(nome='Turma da Catequese')
        resp = self.client.get(self.url)
        self.assertEqual(set(resp.context['form'].fields['turma'].queryset), {self.turma, inativa})
        self.assertContains(resp, 'Antiga (inativa)')

    def test_post_transfere_e_redireciona(self):
        resp = self.client.post(self.url, self.dados, follow=True)
        self.assertRedirects(resp, f"{r('core:ajuste_pastorais')}?pastoral=sementinha")
        self.assertContains(resp, 'Ficha de Ana Souza transferida de Crisma para Sementinha.')
        self.assertFalse(m.CrismaModel.objects.exists())
        nova = m.SementinhaModel.objects.get()
        self.assertEqual(nova.turma, self.turma)
        self.assertEqual(nova.nome_responsavel, 'Maria Souza')
        self.assertFalse(nova.ficha_impressa)

    def test_destino_exige_responsavel(self):
        resp = self.client.post(self.url, {'turma': self.turma.id})
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertIn('nome_responsavel', resp.context['form'].errors)
        self.assertTrue(m.CrismaModel.objects.exists())

    def test_nome_do_responsavel_completo(self):
        resp = self.client.post(self.url, {**self.dados, 'nome_responsavel': 'Maria'})
        self.assertIn('nome_responsavel', resp.context['form'].errors)

    def test_turma_obrigatoria(self):
        resp = self.client.post(self.url, {**self.dados, 'turma': ''})
        self.assertIn('Selecione a turma de destino.', resp.context['form'].errors['turma'])
        self.assertTrue(m.CrismaModel.objects.exists())

    def test_turma_de_outra_pastoral_e_recusada(self):
        outra = m.TurmaCatequeseInfantil.objects.create(nome='Turma da Catequese')
        resp = self.client.post(self.url, {**self.dados, 'turma': outra.id})
        self.assertIn('turma', resp.context['form'].errors)
        self.assertTrue(m.CrismaModel.objects.exists())

    def test_responsavel_vem_preenchido_da_ficha(self):
        self.ficha.nome_responsavel = 'Pedro Souza'
        self.ficha.save()
        resp = self.client.get(self.url)
        self.assertEqual(resp.context['form'].fields['nome_responsavel'].initial, 'Pedro Souza')

    def test_crisma_como_destino_nao_pede_responsavel(self):
        turma = m.TurmaSementinha.objects.create(nome='S')
        ficha = m.SementinhaModel.objects.create(
            nome='Caio Prado', sexo='M', data_nascimento=date(2010, 1, 1), endereco='Rua X',
            cidade='Rio Claro', uf='SP', turma=turma,
            nome_responsavel='Maria Prado', cpf_responsavel='1', endereco_responsavel='Rua X',
        )
        turma_crisma = m.TurmaCrisma.objects.create(nome='Sábado')
        url = r('core:transferir_ficha_pastoral_destino', 'sementinha', ficha.id, 'crisma')
        self.assertNotIn('nome_responsavel', self.client.get(url).context['form'].fields)
        self.client.post(url, {'turma': turma_crisma.id})
        self.assertEqual(m.CrismaModel.objects.get(nome='Caio Prado').nome_responsavel, 'Maria Prado')

    def test_origem_ou_destino_invalidos_retornam_404(self):
        for url in (
            r('core:transferir_ficha_pastoral', 'noivos', self.ficha.id),
            r('core:transferir_ficha_pastoral', 'crisma', 9999),
            r('core:transferir_ficha_pastoral_destino', 'crisma', self.ficha.id, 'crisma'),
            r('core:transferir_ficha_pastoral_destino', 'crisma', self.ficha.id, 'noivos'),
        ):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, HTTPStatus.NOT_FOUND)


class MenuAjustePastoraisTest(TestCase):
    def test_coordenacao_ve_item_entre_total_e_relatorio(self):
        logar(self.client, 'coordenacao', GRUPO_COORDENACAO)
        html = self.client.get(r('core:index')).content.decode()
        total = html.index(f'href="{r("core:total")}"')
        ajuste = html.index(f'href="{r("core:ajuste_pastorais")}"')
        relatorio = html.index(f'href="{r("core:exportar-excel")}"')
        self.assertLess(total, ajuste)
        self.assertLess(ajuste, relatorio)
        self.assertIn('Ajuste entre pastorais', html)

    def test_item_destacado_na_pagina(self):
        logar(self.client, 'coordenacao', GRUPO_COORDENACAO)
        resp = self.client.get(r('core:ajuste_pastorais'))
        self.assertContains(resp, f'class="gc-menu-item ativo" href="{r("core:ajuste_pastorais")}"')

    def test_secretaria_e_visitante_nao_veem_o_item(self):
        self.assertNotContains(self.client.get(r('core:index')), r('core:ajuste_pastorais'))
        logar(self.client, 'secretaria', GRUPO_SECRETARIA)
        self.assertNotContains(self.client.get(r('core:index')), r('core:ajuste_pastorais'))
