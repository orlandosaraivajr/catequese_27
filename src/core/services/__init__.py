"""Geração de fichas em PDF e do relatório em Excel.

Historicamente isso vivia em um único core/services.py com ~3000 linhas,
repetindo o mesmo termo de consentimento LGPD e a mesma autorização de uso de
imagem em 4 lugares diferentes. Está dividido por ministério, com o texto
compartilhado vivendo uma única vez em _common.py -- ver ali para os detalhes.

Este __init__ reexporta as mesmas funções que o services.py antigo expunha,
para que `from .services import gerar_ficha_catequese, ...` em views.py
continue funcionando sem mudanças.
"""
from ._common import data_hoje
from .catequese_infantil import gerar_ficha_catequese
from .crisma import gerar_ficha_crisma, gerar_ficha_crisma_menor, gerar_ficha_crisma_maior
from .perseveranca_mej import (
    gerar_ficha_perseveranca_mej,
    gerar_ficha_perseveranca_mej_menor_idade,
    gerar_ficha_perseveranca_mej_maior_idade,
)
from .catequese_adulto import gerar_ficha_catequese_adulto
from .noivos import gerar_ficha_noivos
from .coroinhas import gerar_ficha_coroinhas
from .excel import gerar_Workbook

__all__ = [
    "data_hoje",
    "gerar_ficha_catequese",
    "gerar_ficha_crisma",
    "gerar_ficha_crisma_menor",
    "gerar_ficha_crisma_maior",
    "gerar_ficha_perseveranca_mej",
    "gerar_ficha_perseveranca_mej_menor_idade",
    "gerar_ficha_perseveranca_mej_maior_idade",
    "gerar_ficha_catequese_adulto",
    "gerar_ficha_noivos",
    "gerar_ficha_coroinhas",
    "gerar_Workbook",
]
