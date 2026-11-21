import os
import tempfile
from datetime import date, timedelta
from http import HTTPStatus
from unittest import mock

from django.shortcuts import resolve_url as r
from django.test import TestCase
from django.utils import timezone

from core import models as m
from core.logs import registrar_log
from core.models import LogFicha
from core.test.acessos import GRUPO_COORDENACAO, GRUPO_SECRETARIA, criar_usuario, logar

BASE = dict(nome='Ana Souza', sexo='F', data_nascimento=date(2014, 1, 1), endereco='Rua X',
            cidade='Rio Claro', uf='SP', nome_responsavel='Maria', cpf_responsavel='1',
            endereco_responsavel='Rua X')

# pastoral -> (modelo, modelo da turma, sufixo das urls, gerador de PDF usado na view)
PASTORAIS = {
    'catequese_infantil': (m.CatequeseInfantilModel, m.TurmaCatequeseInfantil, '', 'gerar_ficha_catequese'),
    'sementinha': (m.SementinhaModel, m.TurmaSementinha, '_sementinha', 'gerar_ficha_sementinha'),
    'crisma': (m.CrismaModel, m.TurmaCrisma, '_crisma', 'gerar_ficha_crisma'),
    'mej': (m.Perseveranca_MEJ_Model, m.TurmaPerseveranca_MEJ, '_perseveranca_mej', 'gerar_ficha_perseveranca_mej'),
    'catequese_adulto': (m.CatequeseAdultoModel, m.TurmaCatequeseAdulto, '_adulto', 'gerar_ficha_catequese_adulto'),
    'noivos': (m.NoivoModel, None, '_noivos', 'gerar_ficha_noivos'),
    'coroinhas': (m.CoroinhaModel, None, '_coroinhas', 'gerar_ficha_coroinhas'),
}


def criar_ficha(pastoral, **extra):
    modelo, turma_model, _, _ = PASTORAIS[pastoral]
    if modelo is m.NoivoModel:
        dados = dict(nome_noivo='João Noivo', nome_noiva='Maria Noiva', data_nascimento_noivo=date(1995, 1, 1),
                     data_nascimento_noiva=date(1996, 1, 1), data_provavel_casamento=date(2027, 5, 1))
    else:
        dados = {campo: valor for campo, valor in BASE.items()
                 if campo in {f.name for f in modelo._meta.fields}}
        if turma_model:
            dados['turma'] = turma_model.objects.create(nome='Turma')
    dados.update(extra)
    return modelo.objects.create(**dados)


def nome_esperado(pastoral):
    return 'João Noivo e Maria Noiva' if pastoral == 'noivos' else 'Ana Souza'


class RegistrarLogTest(TestCase):
    """A função que grava os logs."""

    def test_visitante_fica_sem_autenticacao(self):
        ficha = criar_ficha('crisma')
        log = registrar_log(LogFicha.CADASTRO, ficha)
        self.assertIsNone(log.usuario)
        self.assertEqual(log.usuario_nome, 'sem autenticação')
        self.assertEqual((log.pastoral, log.ficha_id, log.nome_ficha), ('crisma', ficha.pk, 'Ana Souza'))

    def test_usuario_autenticado_e_copiado(self):
        usuario = criar_usuario('joana', GRUPO_SECRETARIA)
        log = registrar_log(LogFicha.ASSINATURA, criar_ficha('noivos'), usuario)
        self.assertEqual(log.usuario, usuario)
        self.assertEqual(log.usuario_nome, 'joana')
        self.assertEqual(log.nome_ficha, 'João Noivo e Maria Noiva')

    def test_log_sobrevive_a_remocao_do_usuario(self):
        usuario = criar_usuario('joana', GRUPO_SECRETARIA)
        log = registrar_log(LogFicha.REMOCAO, criar_ficha('crisma'), usuario)
        usuario.delete()
        log.refresh_from_db()
        self.assertIsNone(log.usuario)
        self.assertEqual(log.usuario_nome, 'joana')


class LogPreCadastroTest(TestCase):
    """Enviar o pré-cadastro (formulário público) gera um log "sem autenticação"."""

    dados_validos = {
        'nome': 'Pedro Souza', 'sexo': 'M', 'data_nascimento': f'{date.today().year - 10}-06-15',
        'endereco': 'Rua São José, 321', 'cidade': 'Araras', 'uf': 'SP',
        'nome_pai': 'José Souza', 'celular_pai': '11988887777',
        'nome_mae': 'Maria Souza', 'celular_mae': '11999996666',
        'nome_responsavel': 'José Souza', 'cpf_responsavel': '123.456.789-00',
        'endereco_responsavel': 'Rua São José, 321',
    }

    def test_envio_valido_registra_cadastro(self):
        self.client.post(r('core:coroinhas'), self.dados_validos)
        ficha = m.CoroinhaModel.objects.get()
        log = LogFicha.objects.get()
        self.assertEqual(log.acao, LogFicha.CADASTRO)
        self.assertEqual((log.pastoral, log.ficha_id, log.nome_ficha), ('coroinhas', ficha.pk, 'Pedro Souza'))
        self.assertIsNone(log.usuario)
        self.assertEqual(log.usuario_nome, LogFicha.SEM_AUTENTICACAO)

    def test_envio_invalido_nao_registra(self):
        self.client.post(r('core:coroinhas'), {'nome': ''})
        self.assertFalse(LogFicha.objects.exists())

    def test_todos_os_formularios_publicos_registram(self):
        """Os 7 formulários usam o mesmo fluxo; basta o form ser válido para haver log."""
        views = {'catequese_infantil': 'CatequeseInfantilForm', 'sementinha': 'SementinhaForm',
                 'crisma': 'CrismaForm', 'perseveranca_mej': 'PerseverancaMejForm',
                 'catequese_adulto': 'CatequeseAdultoForm', 'noivos': 'NoivoForm', 'coroinhas': 'CoroinhaForm'}
        pastoral_da_view = {'perseveranca_mej': 'mej'}
        for view, form in views.items():
            pastoral = pastoral_da_view.get(view, view)
            with self.subTest(view=view):
                ficha = criar_ficha(pastoral)
                with mock.patch(f'core.views.{form}') as form_falso:
                    form_falso.return_value.is_valid.return_value = True
                    form_falso.return_value.save.return_value = ficha
                    self.client.post(r(f'core:{view}'), {})
                self.assertTrue(LogFicha.objects.filter(
                    acao=LogFicha.CADASTRO, pastoral=pastoral, ficha_id=ficha.pk).exists())


class LogSecretariaTest(TestCase):
    """Imprimir, reimprimir, assinar e remover geram log com o usuário da secretaria."""

    def setUp(self):
        self.usuario = logar(self.client, 'joana', GRUPO_SECRETARIA)
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        self.pdf = os.path.join(tmp_dir.name, 'ficha.pdf')
        with open(self.pdf, 'wb') as f:
            f.write(b'%PDF-1.4')

    def imprimir(self, pastoral, ficha):
        _, _, sufixo, gerador = PASTORAIS[pastoral]
        with mock.patch(f'core.views.{gerador}', return_value=self.pdf):
            resp = self.client.post(r(f'core:imprimir_ficha{sufixo}'), {'ficha_id': ficha.pk})
        resp.close()
        return resp

    def assert_log(self, acao, pastoral, ficha_id):
        log = LogFicha.objects.get(acao=acao, pastoral=pastoral, ficha_id=ficha_id)
        self.assertEqual(log.usuario, self.usuario)
        self.assertEqual(log.usuario_nome, 'joana')
        self.assertEqual(log.nome_ficha, nome_esperado(pastoral))
        return log

    def test_impressao_e_reimpressao(self):
        for pastoral in PASTORAIS:
            with self.subTest(pastoral=pastoral):
                ficha = criar_ficha(pastoral)
                self.imprimir(pastoral, ficha)
                self.assert_log(LogFicha.IMPRESSAO, pastoral, ficha.pk)
                self.imprimir(pastoral, ficha)
                self.assert_log(LogFicha.REIMPRESSAO, pastoral, ficha.pk)
                self.assertEqual(LogFicha.objects.filter(pastoral=pastoral, ficha_id=ficha.pk).count(), 2)

    def test_assinatura(self):
        for pastoral, (_, _, sufixo, _) in PASTORAIS.items():
            with self.subTest(pastoral=pastoral):
                ficha = criar_ficha(pastoral)
                self.client.post(r(f'core:assinar_ficha{sufixo}'), {'ficha_id': ficha.pk})
                self.assert_log(LogFicha.ASSINATURA, pastoral, ficha.pk)

    def test_remocao_guarda_nome_e_id_da_ficha_apagada(self):
        for pastoral, (modelo, _, sufixo, _) in PASTORAIS.items():
            with self.subTest(pastoral=pastoral):
                ficha = criar_ficha(pastoral)
                ficha_id = ficha.pk
                self.client.post(r(f'core:remover_ficha{sufixo}'), {'ficha_id': ficha_id})
                self.assertFalse(modelo.objects.filter(pk=ficha_id).exists())
                self.assert_log(LogFicha.REMOCAO, pastoral, ficha_id)

    def test_get_e_ficha_inexistente_nao_registram(self):
        self.client.get(r('core:assinar_ficha_crisma'))
        self.client.post(r('core:remover_ficha_crisma'), {'ficha_id': 999})
        self.assertFalse(LogFicha.objects.exists())

    def test_visitante_nao_gera_log_nas_acoes_da_secretaria(self):
        self.client.logout()
        ficha = criar_ficha('crisma')
        self.client.post(r('core:remover_ficha_crisma'), {'ficha_id': ficha.pk})
        self.assertTrue(m.CrismaModel.objects.filter(pk=ficha.pk).exists())
        self.assertFalse(LogFicha.objects.exists())


class LogTransferenciaTest(TestCase):
    def test_transferencia_registra_origem_e_destino(self):
        usuario = logar(self.client, 'coord', GRUPO_COORDENACAO)
        ficha = criar_ficha('crisma', data_nascimento=date(2021, 6, 1))  # idade de Sementinha
        turma = m.TurmaSementinha.objects.create(nome='Sementinha - Sábado')
        self.client.post(
            r('core:transferir_ficha_pastoral_destino', 'crisma', ficha.pk, 'sementinha'),
            {'turma': turma.id, 'nome_responsavel': 'Maria Souza', 'cpf_responsavel': '123.456.789-00',
             'endereco_responsavel': 'Rua X'},
        )
        nova = m.SementinhaModel.objects.get()
        log = LogFicha.objects.get()
        self.assertEqual(log.acao, LogFicha.TRANSFERENCIA)
        self.assertEqual((log.pastoral, log.ficha_id), ('sementinha', nova.pk))
        self.assertEqual(log.detalhe, f'De Crisma (ficha nº {ficha.pk}) para Sementinha')
        self.assertEqual(log.usuario, usuario)


class TelaLogsAcessoTest(TestCase):
    """Só a coordenação vê a tela de logs."""

    url = r('core:logs_fichas')

    def test_caminho(self):
        self.assertEqual(self.url, '/coordenacao/logs')

    def test_visitante_vai_para_o_login(self):
        resp = self.client.get(self.url)
        self.assertRedirects(resp, f"{r('core:coordenacao')}?next={self.url}", fetch_redirect_response=False)

    def test_secretaria_recebe_acesso_negado(self):
        logar(self.client, 'secretaria', GRUPO_SECRETARIA)
        self.assertEqual(self.client.get(self.url).status_code, HTTPStatus.FORBIDDEN)

    def test_coordenacao_acessa_e_ve_o_botao_no_menu(self):
        logar(self.client, 'coord', GRUPO_COORDENACAO)
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(resp, 'logs_fichas.html')
        self.assertContains(resp, f'href="{self.url}"')

    def test_botao_nao_aparece_para_a_secretaria(self):
        logar(self.client, 'secretaria', GRUPO_SECRETARIA)
        resp = self.client.get(r('core:listar_fichas'))
        self.assertNotContains(resp, f'href="{self.url}"')


class TelaLogsListagemTest(TestCase):
    def setUp(self):
        logar(self.client, 'coord', GRUPO_COORDENACAO)
        self.joana = criar_usuario('joana', GRUPO_SECRETARIA)
        self.ana = criar_ficha('crisma')
        self.pedro = criar_ficha('coroinhas', nome='Pedro Lima')
        registrar_log(LogFicha.CADASTRO, self.ana)
        registrar_log(LogFicha.IMPRESSAO, self.ana, self.joana)
        registrar_log(LogFicha.REMOCAO, self.pedro, self.joana)

    def logs(self, **filtros):
        resp = self.client.get(r('core:logs_fichas'), filtros)
        return list(resp.context['pagina'].object_list)

    def test_lista_tudo_do_mais_recente_para_o_mais_antigo(self):
        self.assertEqual([l.acao for l in self.logs()],
                         [LogFicha.REMOCAO, LogFicha.IMPRESSAO, LogFicha.CADASTRO])

    def test_exibe_dados_do_log(self):
        resp = self.client.get(r('core:logs_fichas'))
        for texto in ('Pré-cadastro enviado', 'Impressão', 'Remoção', 'Crisma', 'Coroinhas',
                      'Ana Souza', 'Pedro Lima', 'joana', 'sem autenticação'):
            self.assertContains(resp, texto)

    def test_filtros(self):
        self.assertEqual(len(self.logs(acao=LogFicha.REMOCAO)), 1)
        self.assertEqual(len(self.logs(pastoral='crisma')), 2)
        self.assertEqual(len(self.logs(usuario='joana')), 2)
        self.assertEqual(len(self.logs(usuario=LogFicha.SEM_AUTENTICACAO)), 1)
        self.assertEqual(len(self.logs(busca='pedro')), 1)
        self.assertEqual(len(self.logs(pastoral='crisma', usuario='joana')), 1)

    def test_filtro_por_periodo(self):
        hoje = timezone.localdate()
        LogFicha.objects.filter(acao=LogFicha.CADASTRO).update(criado_em=timezone.now() - timedelta(days=10))
        self.assertEqual(len(self.logs(de=hoje.isoformat())), 2)
        self.assertEqual(len(self.logs(ate=(hoje - timedelta(days=5)).isoformat())), 1)

    def test_filtro_invalido_e_ignorado(self):
        self.assertEqual(len(self.logs(acao='inexistente', pastoral='xyz')), 3)
        resp = self.client.get(r('core:logs_fichas'), {'de': 'data-errada'})
        self.assertEqual(resp.status_code, HTTPStatus.OK)

    def test_usuarios_do_filtro(self):
        resp = self.client.get(r('core:logs_fichas'))
        self.assertEqual(list(resp.context['usuarios']), ['joana', LogFicha.SEM_AUTENTICACAO])

    def test_paginacao_mantem_filtros(self):
        for _ in range(60):
            registrar_log(LogFicha.ASSINATURA, self.ana, self.joana)
        resp = self.client.get(r('core:logs_fichas'), {'usuario': 'joana'})
        self.assertEqual(len(resp.context['pagina'].object_list), 50)
        self.assertContains(resp, '?usuario=joana&pagina=2')
        resp = self.client.get(r('core:logs_fichas'), {'usuario': 'joana', 'pagina': 2})
        self.assertEqual(len(resp.context['pagina'].object_list), 12)

    def test_tela_somente_leitura(self):
        """Não há como alterar ou apagar logs pela tela."""
        resp = self.client.post(r('core:logs_fichas'))
        self.assertEqual(LogFicha.objects.count(), 3)
        # O único formulário POST da página é o "Sair" do menu.
        self.assertContains(self.client.get(r('core:logs_fichas')), 'method="POST"', count=1)
