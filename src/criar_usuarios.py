"""Cria (ou atualiza) os usuários das áreas restritas.

Uso, de dentro da pasta src/:
    python criar_usuarios.py
"""
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'catequese27.settings')
django.setup()

from django.contrib.auth.models import Group, User  # noqa: E402 (precisa vir depois do setup)

USUARIOS = [
    # (usuário, senha, grupo)
    ('ana.saraiva', 'senha_ana_saraiva', 'coordenacao'),
    ('ana.rubia', 'senha_ana_rubia', 'coordenacao'),
    ('secretaria', 'secretaria27', 'secretaria'),
]

PERMISSAO_ESPERADA = {
    'coordenacao': 'core.acessar_coordenacao',
    'secretaria': 'core.acessar_secretaria',
}


def criar_ou_atualizar(username, senha, nome_grupo):
    grupo = Group.objects.get(name=nome_grupo)  # criado pela migração 0008
    user, criado = User.objects.get_or_create(username=username)
    user.set_password(senha)
    user.is_active = True
    user.save()
    user.groups.add(grupo)

    # Recarrega do banco para não usar o cache de permissões
    user = User.objects.get(pk=user.pk)
    ok = user.has_perm(PERMISSAO_ESPERADA[nome_grupo])
    acao = 'criado' if criado else 'atualizado'
    print(f'{username}: {acao} | grupos={list(user.groups.values_list("name", flat=True))} | acesso ok={ok}')
    return ok


if __name__ == '__main__':
    resultados = [criar_ou_atualizar(*dados) for dados in USUARIOS]
    if not all(resultados):
        raise SystemExit('ATENÇÃO: algum usuário ficou sem o acesso esperado.')
