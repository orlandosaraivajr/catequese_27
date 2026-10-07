"""Controle de acesso às áreas restritas: secretaria e coordenação.

Quem pode o quê é definido por permissões (core.Acesso), entregues aos grupos:

- secretaria:  acessar_secretaria
- coordenacao: acessar_secretaria + acessar_coordenacao

Visitante (não logado) é levado ao login; usuário logado sem a permissão
recebe "Acesso negado" (403).
"""
from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.shortcuts import resolve_url

GRUPO_SECRETARIA = 'secretaria'
GRUPO_COORDENACAO = 'coordenacao'

PERM_SECRETARIA = 'core.acessar_secretaria'
PERM_COORDENACAO = 'core.acessar_coordenacao'

LOGIN_URL = 'core:coordenacao'


def acesso_required(perm):
    def decorator(view_func):
        @wraps(view_func)
        def _view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path(), resolve_url(LOGIN_URL))
            if not request.user.has_perm(perm):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return _view
    return decorator


secretaria_required = acesso_required(PERM_SECRETARIA)
coordenacao_required = acesso_required(PERM_COORDENACAO)


def tem_acesso(user):
    """Usuário tem acesso a alguma área restrita (secretaria ou coordenação)?"""
    return user.has_perm(PERM_SECRETARIA) or user.has_perm(PERM_COORDENACAO)


def pagina_inicial(user):
    """Para onde o usuário vai depois do login (quando não há ?next=)."""
    if user.has_perm(PERM_COORDENACAO):
        return resolve_url('core:dashboard_turmas_catequese')
    return resolve_url('core:listar_fichas')
