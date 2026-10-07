"""Helpers de teste para criar usuários nos grupos de acesso."""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from core.acessos import GRUPO_COORDENACAO, GRUPO_SECRETARIA  # noqa: F401 (reexportados)

SENHA = 'senha12345'


def criar_usuario(username, grupo=None, **extra):
    """Cria um usuário (senha SENHA) e, se informado, o coloca no grupo."""
    user = get_user_model().objects.create_user(username=username, password=SENHA, **extra)
    if grupo:
        user.groups.add(Group.objects.get(name=grupo))
    return user


def logar(client, username, grupo=None, **extra):
    """Cria o usuário no grupo e faz login com ele no client."""
    user = criar_usuario(username, grupo, **extra)
    client.login(username=username, password=SENHA)
    return user
