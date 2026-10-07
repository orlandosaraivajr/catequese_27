# Catequese PNSA

Sistema de pré-inscrição e gestão das pastorais da **Paróquia Nossa Senhora Aparecida** (Rio Claro/SP).

As famílias e os jovens fazem o pré-cadastro na secretaria. A **secretaria** confere, imprime e arquiva as fichas, e a **coordenação** gerencia as turmas e acompanha as inscrições.

### Funcionalidades

- **Pré-inscrição via formulário online:** Catequese Infantil, MEJ, Catequese de Adultos, Noivos e Coroinhas.
- **Turmas gerenciáveis:** horário, limite de vagas, faixa de data de nascimento e turma ativa/inativa, para Catequese Infantil, Crisma, Catequese de Adultos e MEJ.
- **Fichas em PDF:** dados do inscrito, termo LGPD, autorização de imagem e o campo *"Documento verificado por"*, que a secretaria assina.
- **Total de inscrições por turma** e **relatório em Excel**.
- **Acesso por perfil:** veja a tabela abaixo.

| Perfil | O que pode fazer |
|---|---|
| Visitante | Fazer a pré-inscrição |
| Grupo `secretaria` | Listar, imprimir, assinar e remover fichas |
| Grupo `coordenacao` | Tudo da secretaria, mais turmas, total de inscrições e relatórios  |



## Sumário

1. [Pré-requisitos](#1-pré-requisitos)
2. [Baixar o projeto](#2-baixar-o-projeto)
3. [Criar e ativar o ambiente virtual](#3-criar-e-ativar-o-ambiente-virtual)
4. [Instalar as dependências](#4-instalar-as-dependências)
5. [Configurar o arquivo `.env`](#5-configurar-o-arquivo-env)
6. [Criar o banco de dados](#6-criar-o-banco-de-dados)
7. [Criar os grupos `secretaria` e `coordenacao`](#7-criar-os-grupos-secretaria-e-coordenacao)
8. [Criar os usuários `secretaria` e `coordenacao`](#8-criar-os-usuários-secretaria-e-coordenacao)
9. [Rodar o sistema](#9-rodar-o-sistema)
10. [Rodar os testes](#10-rodar-os-testes)
11. [Problemas comuns](#11-problemas-comuns)

---

## 1. Pré-requisitos

| Programa | Versão | Como verificar |
|---|---|---|
| [Python](https://www.python.org/downloads/) | **3.12 ou superior** (exigência do Django 6) | `python --version` (Windows: `py --version`) |
| [Git](https://git-scm.com/downloads) | qualquer versão recente | `git --version` |

**Linux (Ubuntu/Debian):**

```console
sudo apt update
sudo apt install python3 python3-venv python3-pip git
```

**Windows:**

1. Baixe e instale o Python em <https://www.python.org/downloads/>. Na primeira tela do instalador, marque **"Add python.exe to PATH"**.
2. Baixe e instale o Git em <https://git-scm.com/downloads>. Pode aceitar as opções padrão.
3. Abra o **PowerShell** ou o **Prompt de Comando (cmd)** para digitar os comandos abaixo.

> No Linux, use `python3` onde este guia diz `python`. No Windows, se `python` não funcionar, use `py`.

## 2. Baixar o projeto

Linux e Windows:

```console
git clone https://github.com/orlandosaraivajr/catequese_27.git
cd catequese_27
```

## 3. Criar e ativar o ambiente virtual

O ambiente virtual (`venv`) isola as bibliotecas deste projeto das do resto do computador.

**Linux:**

```console
python3 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell):**

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (Prompt de Comando - cmd):**

```bat
py -m venv venv
venv\Scripts\activate.bat
```

Com o ambiente ativado, o terminal mostra `(venv)` no começo da linha.

> **Sempre ative o ambiente virtual** antes de trabalhar no projeto, sempre que abrir um terminal novo. Para desativar, digite `deactivate`.

## 4. Instalar as dependências

Com o `(venv)` ativo, no Linux e no Windows:

```console
pip install -r requirements.txt
```

## 5. Configurar o arquivo `.env`

As configurações (chave secreta, modo de depuração e banco de dados) ficam no arquivo `src/.env`, que **não vai para o Git**. Crie esse arquivo a partir do modelo `src/env.example`:

**Linux:**

```console
cd src
cp env.example .env
```

**Windows (PowerShell):**

```powershell
cd src
Copy-Item env.example .env
```

**Windows (cmd):**

```bat
cd src
copy env.example .env
```

Agora **gere uma chave secreta nova** (não use a do modelo):

```console
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Abra o arquivo `src/.env` num editor de texto (Bloco de Notas, VS Code etc.) e deixe-o assim:

```ini
SECRET_KEY='cole-aqui-a-chave-gerada-entre-aspas-simples'
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///catequese.sqlite3
```

| Variável | Para que serve |
|---|---|
| `SECRET_KEY` | Chave de segurança do Django. Mantenha as aspas simples, porque a chave pode ter caracteres especiais. |
| `DEBUG` | `True` no seu computador (mostra erros detalhados e serve o CSS do `/admin/`). **Em produção, sempre `False`.** |
| `ALLOWED_HOSTS` | Endereços pelos quais o sistema pode ser acessado, separados por vírgula. |
| `DATABASE_URL` | Banco de dados. O padrão é um arquivo SQLite, `src/catequese.sqlite3`, criado automaticamente. |

> **Daqui em diante, todos os comandos são executados dentro da pasta `src`**, onde fica o `manage.py`.

## 6. Criar o banco de dados

```console
python manage.py migrate
```

Esse comando cria as tabelas, as turmas iniciais e os grupos de acesso (próximo passo).

Crie também um **superusuário**, o administrador geral que acessa o painel `/admin/`:

```console
python manage.py createsuperuser
```

Informe nome de usuário, e-mail (pode deixar em branco) e senha. A senha não aparece enquanto você digita, e isso é normal.

## 7. Criar os grupos `secretaria` e `coordenacao`

**Os grupos são criados automaticamente pelo `migrate`** do passo 6, já com as permissões corretas:

| Grupo | Permissões |
|---|---|
| `secretaria` | `acessar_secretaria` |
| `coordenacao` | `acessar_secretaria` e `acessar_coordenacao` |

Para **conferir** se eles existem:

```console
python manage.py shell -c "from django.contrib.auth.models import Group; [print(g.name, list(g.permissions.values_list('codename', flat=True))) for g in Group.objects.all()]"
```

Saída esperada:

```
secretaria ['acessar_secretaria']
coordenacao ['acessar_coordenacao', 'acessar_secretaria']
```

<details>
<summary><b>Se os grupos não aparecerem</b>: criar manualmente</summary>

Abra o shell do Django:

```console
python manage.py shell
```

Cole os comandos abaixo e tecle Enter:

```python
from django.contrib.auth.models import Group, Permission

perm_secretaria = Permission.objects.get(content_type__app_label='core', codename='acessar_secretaria')
perm_coordenacao = Permission.objects.get(content_type__app_label='core', codename='acessar_coordenacao')

secretaria, _ = Group.objects.get_or_create(name='secretaria')
secretaria.permissions.set([perm_secretaria])

coordenacao, _ = Group.objects.get_or_create(name='coordenacao')
coordenacao.permissions.set([perm_secretaria, perm_coordenacao])
```

Digite `exit()` para sair do shell.

Se aparecer o erro `Permission matching query does not exist`, é porque as migrações não foram aplicadas. Volte ao passo 6 e rode `python manage.py migrate`.

</details>

## 8. Criar os usuários `secretaria` e `coordenacao`

Abra o shell do Django:

```console
python manage.py shell
```

Cole os comandos abaixo. O sistema vai **pedir a senha de cada usuário**, e ela não aparece enquanto você digita:

```python
from django.contrib.auth.models import User, Group
from getpass import getpass

# Usuário "secretaria", no grupo secretaria
secretaria = User.objects.create_user('secretaria', password=getpass('Senha do usuário secretaria: '))
secretaria.groups.add(Group.objects.get(name='secretaria'))

# Usuário "coordenacao", no grupo coordenacao
coordenacao = User.objects.create_user('coordenacao', password=getpass('Senha do usuário coordenacao: '))
coordenacao.groups.add(Group.objects.get(name='coordenacao'))
```

Para conferir, ainda dentro do shell:

```python
for u in User.objects.all():
    print(u.username, list(u.groups.values_list('name', flat=True)))
```

Saída esperada (além do superusuário criado no passo 6):

```
secretaria ['secretaria']
coordenacao ['coordenacao']
```

Digite `exit()` para sair do shell.

> **Importante:** o usuário precisa **estar no grupo** para entrar no sistema. Um usuário sem grupo vê a mensagem *"Este usuário não tem acesso à área restrita"* ao tentar o login.

### Outras operações úteis

**Trocar a senha de um usuário:**

```console
python manage.py changepassword secretaria
```

**Colocar um usuário que já existe num grupo** (por exemplo, `maria` na secretaria):

```console
python manage.py shell -c "from django.contrib.auth.models import User, Group; User.objects.get(username='maria').groups.add(Group.objects.get(name='secretaria'))"
```

**Pelo painel `/admin/`:** entre com o superusuário, vá em **Usuários**, abra o usuário, mova o grupo desejado no campo **Grupos** para a caixa da direita e clique em **Salvar**.

## 9. Rodar o sistema

```console
python manage.py runserver
```

Abra no navegador:

| Endereço | O que é |
|---|---|
| <http://127.0.0.1:8000/> | Página inicial: pré-inscrição pública |
| <http://127.0.0.1:8000/coordenacao> | Login da secretaria e da coordenação |
| <http://127.0.0.1:8000/secretaria> | Fichas pendentes (secretaria e coordenação) |
| <http://127.0.0.1:8000/coordenacao/turmas_catequese> | Turmas (coordenação) |
| <http://127.0.0.1:8000/admin/> | Painel administrativo do Django (superusuário) |

Depois do login, a **secretaria** vai para a lista de fichas e a **coordenação** vai para as turmas.

Para parar o servidor, tecle **Ctrl + C** no terminal.

## 10. Rodar os testes

```console
python manage.py test
```

Ao final deve aparecer `OK`. Opcionalmente, para ver a cobertura de testes:

```console
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

O relatório `coverage html` é gerado na pasta `htmlcov/`. Abra o arquivo `index.html` no navegador.

## 11. Problemas comuns

| Problema | Solução |
|---|---|
| `ImproperlyConfigured: Set the SECRET_KEY environment variable` | O arquivo `src/.env` não existe ou está sem `SECRET_KEY`. Refaça o passo 5. |
| `python: command not found` (Linux) | Use `python3`. |
| `'python' não é reconhecido...` (Windows) | Use `py`, ou reinstale o Python marcando **"Add python.exe to PATH"**. |
| PowerShell: *"a execução de scripts foi desabilitada neste sistema"* ao ativar o venv | Rode uma vez `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, confirme com `S` e ative de novo. Ou use o Prompt de Comando (cmd). |
| `ModuleNotFoundError: No module named 'django'` | O ambiente virtual não está ativo. Ative-o (passo 3). |
| `/admin/` aparece sem formatação (sem CSS) | Use `DEBUG=True` no `src/.env`. Com `DEBUG=False`, o `runserver` não serve os arquivos estáticos (ou rode `python manage.py runserver --insecure`). |
| *"Este usuário não tem acesso à área restrita"* | O usuário não está em nenhum grupo. Veja o passo 8. |
| `can't open file 'manage.py'` | Você não está na pasta `src`. Rode `cd src`. |

---

## Estrutura do projeto

```
catequese_27/
├── requirements.txt        # dependências Python
├── README.md
└── src/                    # rode os comandos daqui
    ├── manage.py
    ├── env.example         # modelo do .env
    ├── catequese27/        # configurações do Django (settings, urls)
    ├── core/               # aplicação principal
    │   ├── models.py       # fichas, turmas e permissões de acesso
    │   ├── views.py        # páginas
    │   ├── forms.py        # formulários e validações
    │   ├── acessos.py      # regras de acesso (secretaria / coordenação)
    │   ├── services/       # geração dos PDFs e do Excel
    │   ├── templates/      # HTML
    │   ├── migrations/     # banco de dados (inclui a criação dos grupos)
    │   └── test/           # testes automatizados
    └── static/pdf/         # imagem do cabeçalho das fichas
```
