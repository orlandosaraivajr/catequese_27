from django.db import migrations

PERMISSOES = {
    'acessar_secretaria': 'Pode acessar a secretaria (listar, imprimir, assinar e remover fichas)',
    'acessar_coordenacao': 'Pode acessar a coordenação (turmas, totais e relatório)',
}
GRUPOS = {
    'secretaria': ['acessar_secretaria'],
    'coordenacao': ['acessar_secretaria', 'acessar_coordenacao'],
}


def criar_grupos(apps, schema_editor):
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Permission = apps.get_model('auth', 'Permission')
    Group = apps.get_model('auth', 'Group')
    User = apps.get_model('auth', 'User')

    # As permissões normalmente só são criadas no post_migrate; aqui precisamos delas já.
    ct, _ = ContentType.objects.get_or_create(app_label='core', model='acesso')
    perms = {
        codename: Permission.objects.get_or_create(
            codename=codename, content_type=ct, defaults={'name': nome},
        )[0]
        for codename, nome in PERMISSOES.items()
    }
    for nome, codenames in GRUPOS.items():
        grupo, _ = Group.objects.get_or_create(name=nome)
        grupo.permissions.add(*[perms[c] for c in codenames])

    # Antes, o acesso à coordenação era "ser staff": quem já era staff continua com acesso.
    coordenacao = Group.objects.get(name='coordenacao')
    for user in User.objects.filter(is_staff=True, is_active=True):
        user.groups.add(coordenacao)


def remover_grupos(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    Group.objects.filter(name__in=GRUPOS).delete()
    Permission.objects.filter(content_type__app_label='core', codename__in=PERMISSOES).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_turmaperseveranca_mej'),
        ('auth', '__latest__'),
        ('contenttypes', '__latest__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Acesso',
            fields=[],
            options={
                'managed': False,
                'default_permissions': (),
                'permissions': [(codename, nome) for codename, nome in PERMISSOES.items()],
            },
        ),
        migrations.RunPython(criar_grupos, remover_grupos),
    ]
