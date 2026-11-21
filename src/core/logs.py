"""Registro das ações sobre as fichas na tabela LogFicha.

As views chamam ``registrar_log`` explicitamente (em vez de signals) porque
precisam informar quem fez a ação (``request.user``) e qual foi ela:
impressão, reimpressão e assinatura são, todas, um simples ``save()``.
"""
from .models import (
    CatequeseAdultoModel, CatequeseInfantilModel, CoroinhaModel, CrismaModel, LogFicha,
    NoivoModel, Perseveranca_MEJ_Model, SementinhaModel,
)

PASTORAL_POR_MODELO = {
    CatequeseInfantilModel: 'catequese_infantil',
    SementinhaModel: 'sementinha',
    CrismaModel: 'crisma',
    Perseveranca_MEJ_Model: 'mej',
    CatequeseAdultoModel: 'catequese_adulto',
    NoivoModel: 'noivos',
    CoroinhaModel: 'coroinhas',
}


def nome_da_ficha(ficha):
    """Nome exibido no log; a ficha de noivos tem dois nomes."""
    if isinstance(ficha, NoivoModel):
        return f"{ficha.nome_noivo} e {ficha.nome_noiva}"
    return ficha.nome


def registrar_log(acao, ficha, usuario=None, detalhe=''):
    """Grava uma linha em LogFicha. Deve ser chamada ANTES de apagar a ficha.

    ``usuario`` não autenticado (ou ausente) é registrado como "sem autenticação".
    """
    autenticado = usuario is not None and usuario.is_authenticated
    return LogFicha.objects.create(
        acao=acao,
        pastoral=PASTORAL_POR_MODELO[type(ficha)],
        ficha_id=ficha.pk,
        nome_ficha=nome_da_ficha(ficha)[:310],
        detalhe=detalhe[:255],
        usuario=usuario if autenticado else None,
        usuario_nome=usuario.get_username() if autenticado else LogFicha.SEM_AUTENTICACAO,
    )
