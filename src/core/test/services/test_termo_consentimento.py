import tempfile
from unittest import mock

from django.test import TestCase, override_settings

from core.services import _common
from core.test.services.test_autorizacao_imagem import FICHAS_MAIOR, FICHAS_MENOR
from core.test.services.test_gerar_ficha_crisma import textos_por_pagina
from core.test.services.test_verificacao_secretaria import fichas

PAGINA_TERMO_CONSENTIMENTO = 2

# Trechos vigentes do termo de consentimento LGPD da Paróquia.
# Se algum teste falhar, o texto do termo mudou: confirme se foi intencional.
REVOGACAO = (
    'A revogação não terá efeito retroativo, não implicando a obrigatoriedade de retirada de materiais já '
    'publicados ou distribuídos até a data da notificação, mas impedindo novas utilizações.'
)
ECA = 'Estatuto da Criança e do Adolescente – ECA (Lei nº 8.069/90)'


class TermoConsentimentoTest(TestCase):
    """Termo de consentimento LGPD da Paróquia (página 2): revogação e ECA."""

    def setUp(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        self.media_root = tmp_dir.name

    def termo(self, nome):
        _, gerador, ficha = fichas()[nome]
        textos = textos_por_pagina(gerador, ficha, self.media_root)
        return ' '.join(t for pagina, t in textos if pagina == PAGINA_TERMO_CONSENTIMENTO)

    def test_termo_continua_sendo_da_paroquia(self):
        for nome in fichas():
            with self.subTest(ficha=nome):
                self.assertIn('PARÓQUIA NOSSA SENHORA APARECIDA', self.termo(nome))

    def test_revogacao_sem_efeito_retroativo_em_todas_as_fichas(self):
        for nome in fichas():
            with self.subTest(ficha=nome):
                texto = self.termo(nome)
                self.assertIn('revogar este consentimento a qualquer momento', texto)
                self.assertIn(REVOGACAO, texto)

    def test_revogacao_no_plural_para_os_noivos(self):
        self.assertIn('7) Declaramos, ainda, estarmos cientes de que podemos revogar', self.termo('noivos'))

    def test_eca_apenas_nos_termos_de_menores(self):
        for nome in FICHAS_MENOR:
            with self.subTest(ficha=nome):
                texto = self.termo(nome)
                self.assertIn(ECA, texto)
                self.assertIn('8) A CONTROLADORA se compromete a zelar pela proteção integral de crianças e adolescentes', texto)
        for nome in (*FICHAS_MAIOR, 'noivos'):
            with self.subTest(ficha=nome):
                texto = self.termo(nome)
                self.assertNotIn('ECA', texto)
                self.assertNotIn('8.069', texto)

    def test_texto_cabe_na_pagina_e_sobra_espaco_para_assinatura(self):
        for nome in fichas():
            with self.subTest(ficha=nome):
                retornos = []
                original = _common.desenhar_texto_em_fluxo

                def espiao(*args, **kwargs):
                    retornos.append(original(*args, **kwargs))
                    return retornos[-1]

                modulo, gerador, ficha = fichas()[nome]
                with mock.patch('core.services._common.desenhar_texto_em_fluxo', side_effect=espiao), \
                     mock.patch(f'core.services.{modulo}.desenhar_texto_em_fluxo', side_effect=espiao,
                                create=True), \
                     override_settings(MEDIA_ROOT=self.media_root):
                    gerador(ficha)
                # 1º retorno = termo de consentimento (página 2); a assinatura ocupa ≈ 76pt abaixo dele.
                self.assertGreater(retornos[0] - 76, 30)
