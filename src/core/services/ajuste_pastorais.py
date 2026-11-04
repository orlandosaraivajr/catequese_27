"""Ajuste entre pastorais: transfere uma ficha de uma pastoral para outra.

Usado pela coordenação para corrigir cadastros feitos no formulário errado
(ex.: uma criança inscrita na Crisma que deveria estar na Sementinha).

A transferência cria a ficha no destino com os campos em comum, apaga a ficha
de origem (tudo numa transação) e devolve a ficha nova. Nenhuma outra tabela
aponta para as fichas, então não há referências a atualizar.
"""
from datetime import date

from django.db import transaction

from core.models import (
    CatequeseInfantilModel, CrismaModel, Perseveranca_MEJ_Model, SementinhaModel,
    TurmaCatequeseInfantil, TurmaCrisma, TurmaPerseveranca_MEJ, TurmaSementinha,
)

# Pastorais entre as quais é possível transferir fichas (todas têm turma e
# praticamente os mesmos campos). ``exige_responsavel``: o destino precisa de
# nome, CPF e endereço do responsável (usados nos termos do PDF).
PASTORAIS_AJUSTE = {
    'catequese_infantil': {
        'titulo': 'Catequese Infantil', 'modelo': CatequeseInfantilModel,
        'turma': TurmaCatequeseInfantil, 'exige_responsavel': True,
    },
    'sementinha': {
        'titulo': 'Sementinha', 'modelo': SementinhaModel,
        'turma': TurmaSementinha, 'exige_responsavel': True,
    },
    'crisma': {
        'titulo': 'Crisma', 'modelo': CrismaModel,
        'turma': TurmaCrisma, 'exige_responsavel': False,
    },
    'mej': {
        'titulo': 'MEJ', 'modelo': Perseveranca_MEJ_Model,
        'turma': TurmaPerseveranca_MEJ, 'exige_responsavel': True,
    },
}

CAMPOS_RESPONSAVEL = ('nome_responsavel', 'cpf_responsavel', 'endereco_responsavel')

# Não são copiados: a turma é escolhida no destino e a ficha volta a ficar
# pendente, para a secretaria imprimir a ficha do formulário certo.
CAMPOS_NAO_COPIADOS = {'id', 'turma', 'ficha_impressa', 'ficha_assinada'}


def _campos(modelo):
    return {
        campo.name: campo for campo in modelo._meta.concrete_fields
        if campo.name not in CAMPOS_NAO_COPIADOS
    }


def _formatar(valor):
    if valor is True:
        return 'Sim'
    if isinstance(valor, date):
        return valor.strftime('%d/%m/%Y')
    return str(valor)


def campos_perdidos(ficha, modelo_destino):
    """[(campo, valor)] dos dados preenchidos na ficha que não existem no destino."""
    destino = _campos(modelo_destino)
    perdidos = []
    for nome, campo in _campos(type(ficha)).items():
        valor = getattr(ficha, nome)
        if nome in destino or valor in (None, '', False):
            continue
        perdidos.append((campo.verbose_name.capitalize(), _formatar(valor)))
    return perdidos


def transferir_ficha(ficha, modelo_destino, turma, **dados):
    """Cria a ficha em ``modelo_destino`` na ``turma`` e apaga a de origem.

    ``dados`` sobrescreve campos da ficha nova (ex.: os dados do responsável).
    """
    comuns = _campos(type(ficha)).keys() & _campos(modelo_destino).keys()
    nova = modelo_destino(turma=turma, **{nome: getattr(ficha, nome) for nome in comuns})
    for nome, valor in dados.items():
        setattr(nova, nome, valor)
    with transaction.atomic():
        nova.save()
        ficha.delete()
    return nova
