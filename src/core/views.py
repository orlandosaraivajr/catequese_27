from django.shortcuts import render, redirect, get_object_or_404, resolve_url
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.views.csrf import csrf_failure
from django.contrib import messages
from django.utils.timezone import localtime
from django.http import HttpResponse, FileResponse, Http404
from django.db.models import Count
from .forms import CatequeseInfantilForm, SementinhaForm, CrismaForm, PerseverancaMejForm, CatequeseAdultoForm, NoivoForm, CoroinhaForm, TurmaForm, TurmaSementinhaForm, TurmaCrismaForm, TurmaCatequeseAdultoForm, TurmaPerseveranca_MEJForm, AjustePastoralForm, CoordenacaoLoginForm
from .models import CatequeseInfantilModel, SementinhaModel, CrismaModel, Perseveranca_MEJ_Model, CatequeseAdultoModel, NoivoModel, CoroinhaModel, TurmaCatequeseInfantil, TurmaSementinha, TurmaCrisma, TurmaCatequeseAdulto, TurmaPerseveranca_MEJ
from .services import gerar_ficha_catequese, gerar_ficha_sementinha, gerar_ficha_crisma, gerar_ficha_perseveranca_mej
from .acessos import coordenacao_required, secretaria_required, tem_acesso, pagina_inicial
from .services import gerar_ficha_catequese_adulto, gerar_ficha_noivos ,  gerar_Workbook, gerar_Workbook_casamento, gerar_Workbook_coroinhas, gerar_ficha_coroinhas
from .services.ajuste_pastorais import PASTORAIS_AJUSTE, CAMPOS_RESPONSAVEL, campos_perdidos, transferir_ficha
from datetime import date
from django.core.paginator import Paginator
from django.db import transaction
from .models import LogFicha
from .logs import registrar_log


def index(request):
    return render(request, 'index.html')

def _pre_cadastro(request, form_class, template):
    """Formulário público de pré-cadastro; registra no log o envio da ficha."""
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            ficha = form.save()
            registrar_log(LogFicha.CADASTRO, ficha, request.user)
            return redirect('core:procure_secretaria')
    else:
        form = form_class()
    return render(request, template, {'form': form})

def catequese_infantil(request):
    return _pre_cadastro(request, CatequeseInfantilForm, 'catequese_infantil.html')

def sementinha(request):
    return _pre_cadastro(request, SementinhaForm, 'sementinha.html')

def crisma(request):
    return _pre_cadastro(request, CrismaForm, 'crisma.html')

def perseveranca_mej(request):
    return _pre_cadastro(request, PerseverancaMejForm, 'perseveranca.html')

def catequese_adulto(request):
    return _pre_cadastro(request, CatequeseAdultoForm, 'catequese_adulto.html')

def noivos(request):
    return _pre_cadastro(request, NoivoForm, 'noivos.html')

def coroinhas(request):
    return _pre_cadastro(request, CoroinhaForm, 'coroinhas.html')

def procure_secretaria(request):
    return render(request, 'procure_secretaria.html')

@secretaria_required
def listar_fichas(request):
    fichas = CatequeseInfantilModel.objects.filter(ficha_impressa=False).filter(ficha_assinada=False).order_by('nome')
    fichasSementinha = SementinhaModel.objects.filter(ficha_impressa=False).filter(ficha_assinada=False).order_by('nome')
    fichasCrisma = CrismaModel.objects.filter(ficha_impressa=False).filter(ficha_assinada=False).order_by('nome')
    fichasMEJ = Perseveranca_MEJ_Model.objects.filter(ficha_impressa=False).filter(ficha_assinada=False).order_by('nome')
    fichasAdultos = CatequeseAdultoModel.objects.filter(ficha_impressa=False).filter(ficha_assinada=False).order_by('nome')
    fichasNoivos = NoivoModel.objects.filter(ficha_impressa=False).filter(ficha_assinada=False).order_by('nome_noivo')
    fichasCoroinhas = CoroinhaModel.objects.filter(ficha_impressa=False).filter(ficha_assinada=False).order_by('nome')
    mensagem = 'Fichas Pendentes de Impressão'
    contexto = {'fichas': fichas,'fichasSementinha': fichasSementinha,'fichasCrisma': fichasCrisma, 
                'fichasMEJ': fichasMEJ,'fichasAdultos': fichasAdultos,
                'fichasNoivos': fichasNoivos,
                'fichasCoroinhas': fichasCoroinhas,
                'mensagem': mensagem}
    return render(request, 'listar_fichas.html', contexto)

@secretaria_required
def listar_todas_fichas(request):
    fichas = CatequeseInfantilModel.objects.all().filter(ficha_assinada=False).order_by('nome')
    fichasSementinha = SementinhaModel.objects.all().filter(ficha_assinada=False).order_by('nome')
    fichasCrisma = CrismaModel.objects.all().filter(ficha_assinada=False).order_by('nome')
    fichasMEJ = Perseveranca_MEJ_Model.objects.all().filter(ficha_assinada=False).order_by('nome')
    fichasAdultos = CatequeseAdultoModel.objects.all().filter(ficha_assinada=False).order_by('nome')
    fichasNoivos = NoivoModel.objects.all().filter(ficha_assinada=False).order_by('nome_noivo')
    fichasCoroinhas = CoroinhaModel.objects.all().filter(ficha_assinada=False).order_by('nome')
    mensagem = 'Fichas Pendentes de Impressão'
    contexto = {'fichas': fichas,'fichasSementinha': fichasSementinha,'fichasCrisma': fichasCrisma, 
                'fichasMEJ': fichasMEJ,'fichasAdultos': fichasAdultos,
                'fichasNoivos': fichasNoivos,
                'fichasCoroinhas': fichasCoroinhas,
                'mensagem': mensagem}
    return render(request, 'listar_fichas.html', contexto)

# ---------------------------------------------------------------------------
# Secretaria: imprimir / assinar / remover fichas
#
# As 21 views abaixo só escolhem o modelo (e o gerador de PDF); o trabalho e
# o registro no log ficam nestes três helpers. O gerador é passado na chamada
# (e não guardado num dicionário) para continuar "patchável" nos testes.
# ---------------------------------------------------------------------------

def _imprimir(request, modelo, gerador):
    if request.method == 'POST':
        ficha = get_object_or_404(modelo, id=request.POST.get('ficha_id'))
        acao = LogFicha.REIMPRESSAO if ficha.ficha_impressa else LogFicha.IMPRESSAO
        ficha.ficha_impressa = True
        ficha.save()
        registrar_log(acao, ficha, request.user)
        pdf_path = gerador(ficha)
        return FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')
    return redirect('core:listar_fichas')

def _assinar(request, modelo):
    if request.method == 'POST':
        ficha = get_object_or_404(modelo, id=request.POST.get('ficha_id'))
        ficha.ficha_assinada = True
        ficha.save()
        registrar_log(LogFicha.ASSINATURA, ficha, request.user)
    return redirect('core:listar_fichas')

def _remover(request, modelo):
    if request.method == 'POST':
        ficha = get_object_or_404(modelo, id=request.POST.get('ficha_id'))
        with transaction.atomic():
            registrar_log(LogFicha.REMOCAO, ficha, request.user)  # antes: depois do delete não há id
            ficha.delete()
    return redirect('core:listar_fichas')

@secretaria_required
def imprimir_ficha(request):
    return _imprimir(request, CatequeseInfantilModel, gerar_ficha_catequese)

@secretaria_required
def assinar_ficha(request):
    return _assinar(request, CatequeseInfantilModel)

@secretaria_required
def remover_ficha(request):
    return _remover(request, CatequeseInfantilModel)

@secretaria_required
def imprimir_ficha_sementinha(request):
    return _imprimir(request, SementinhaModel, gerar_ficha_sementinha)

@secretaria_required
def assinar_ficha_sementinha(request):
    return _assinar(request, SementinhaModel)

@secretaria_required
def remover_ficha_sementinha(request):
    return _remover(request, SementinhaModel)

@secretaria_required
def imprimir_ficha_crisma(request):
    return _imprimir(request, CrismaModel, gerar_ficha_crisma)

@secretaria_required
def assinar_ficha_crisma(request):
    return _assinar(request, CrismaModel)

@secretaria_required
def remover_ficha_crisma(request):
    return _remover(request, CrismaModel)

@secretaria_required
def imprimir_ficha_perseveranca_mej(request):
    return _imprimir(request, Perseveranca_MEJ_Model, gerar_ficha_perseveranca_mej)

@secretaria_required
def assinar_ficha_perseveranca_mej(request):
    return _assinar(request, Perseveranca_MEJ_Model)

@secretaria_required
def remover_ficha_perseveranca_mej(request):
    return _remover(request, Perseveranca_MEJ_Model)

@secretaria_required
def imprimir_ficha_adulto(request):
    return _imprimir(request, CatequeseAdultoModel, gerar_ficha_catequese_adulto)

@secretaria_required
def assinar_ficha_adulto(request):
    return _assinar(request, CatequeseAdultoModel)

@secretaria_required
def remover_ficha_adulto(request):
    return _remover(request, CatequeseAdultoModel)

@secretaria_required
def imprimir_ficha_noivos(request):
    return _imprimir(request, NoivoModel, gerar_ficha_noivos)

@secretaria_required
def assinar_ficha_noivos(request):
    return _assinar(request, NoivoModel)

@secretaria_required
def remover_ficha_noivos(request):
    return _remover(request, NoivoModel)

@secretaria_required
def imprimir_ficha_coroinhas(request):
    return _imprimir(request, CoroinhaModel, gerar_ficha_coroinhas)

@secretaria_required
def assinar_ficha_coroinhas(request):
    return _assinar(request, CoroinhaModel)

@secretaria_required
def remover_ficha_coroinhas(request):
    return _remover(request, CoroinhaModel)

@coordenacao_required
def total(request):
    # Catequese Infantil
    qs = (
        CatequeseInfantilModel.objects
        .values('turma__nome')
        .annotate(quantidade=Count('id'))
        .order_by('-quantidade')
    )
    total_catequese_infantil = [
        {
            "titulo": item["turma__nome"],
            "quantidade": item["quantidade"]
        }
        for item in qs
    ]
    # Sementinha
    qs = (
        SementinhaModel.objects
        .values('turma__nome')
        .annotate(quantidade=Count('id'))
        .order_by('-quantidade')
    )
    total_sementinha = [
        {
            "titulo": item["turma__nome"],
            "quantidade": item["quantidade"]
        }
        for item in qs
    ]
    # Crisma
    qs = (
        CrismaModel.objects
        .values('turma__nome')
        .annotate(quantidade=Count('id'))
        .order_by('-quantidade')
    )
    total_crisma = [
        {
            "titulo": item["turma__nome"],
            "quantidade": item["quantidade"]
        }
        for item in qs
    ]
    # Perseverança / MEJ
    qs = (
        Perseveranca_MEJ_Model.objects
        .values('turma__nome')
        .annotate(quantidade=Count('id'))
        .order_by('-quantidade')
    )
    total_perseveranca_mej = [
        {
            "titulo": item["turma__nome"],
            "quantidade": item["quantidade"]
        }
        for item in qs
    ]
    # Catequese Adulto
    qs = (
        CatequeseAdultoModel.objects
        .values('turma__nome')
        .annotate(quantidade=Count('id'))
        .order_by('-quantidade')
    )
    total_catequese_adulto = [
        {
            "titulo": item["turma__nome"],
            "quantidade": item["quantidade"]
        }
        for item in qs
    ]

    contexto = {
        'mensagem': 'Relatório de Inscrições por Horário',
        'total_catequese_infantil': total_catequese_infantil,
        'total_sementinha': total_sementinha,
        'total_crisma': total_crisma,
        'total_perseveranca_mej': total_perseveranca_mej,
        'total_catequese_adulto': total_catequese_adulto,
    }
    return render(request, 'contador_fichas.html', contexto)

@secretaria_required
def exportar_excel(request):
    wb = gerar_Workbook()
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    file_name = 'relatorio_catequese_' + localtime().strftime('%d_%m_%Y__%Hh_%Mm')
    response['Content-Disposition'] = 'attachment; filename=' + file_name + '.xlsx'
    wb.save(response)
    return response

@secretaria_required
def exportar_excel_casamento(request):
    wb = gerar_Workbook_casamento()
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    file_name = 'relatorio_casamento_' + localtime().strftime('%d_%m_%Y__%Hh_%Mm')
    response['Content-Disposition'] = 'attachment; filename=' + file_name + '.xlsx'
    wb.save(response)
    return response

@secretaria_required
def exportar_excel_coroinhas(request):
    wb = gerar_Workbook_coroinhas()
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    file_name = 'relatorio_coroinhas_' + localtime().strftime('%d_%m_%Y__%Hh_%Mm')
    response['Content-Disposition'] = 'attachment; filename=' + file_name + '.xlsx'
    wb.save(response)
    return response


# ---------------------------------------------------------------------------
# Login / logout da área restrita (secretaria e coordenação)
# ---------------------------------------------------------------------------

class CoordenacaoLoginView(LoginView):
    template_name = 'coordenacao_login.html'
    authentication_form = CoordenacaoLoginForm

    def dispatch(self, request, *args, **kwargs):
        # Secretaria/coordenação já logada vai direto para a sua página inicial.
        # (Usuário sem acesso logado vê o formulário, evitando loop de redirect.)
        if request.user.is_authenticated and tem_acesso(request.user):
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)

    def get_default_redirect_url(self):
        # Sem ?next=, a coordenação vai para as turmas e a secretaria para as fichas.
        return pagina_inicial(self.request.user)


def csrf_falhou(request, reason=''):
    # Formulário de login aberto antes de outro login no mesmo navegador (outra aba,
    # recarga automática da secretaria) tem token vencido. Basta abrir a tela de novo:
    # quem já está logado segue para a sua página inicial.
    if request.path == resolve_url('core:coordenacao'):
        messages.warning(request, 'A página de login estava desatualizada. Se necessário, entre novamente.')
        return redirect(request.get_full_path())
    return csrf_failure(request, reason=reason)


def coordenacao_logout(request):
    if request.method != 'POST':
        # GET não desloga (evita logout forçado via link/imagem de outro site);
        # apenas leva de volta à área da coordenação.
        return redirect('core:coordenacao')
    logout(request)
    messages.info(request, 'Você saiu da área da coordenação.')
    return redirect('core:coordenacao')


# ---------------------------------------------------------------------------
# Dashboard da coordenação -- turmas da Catequese Infantil, Sementinha, Crisma,
# Catequese de Adultos e Perseverança / MEJ
# ---------------------------------------------------------------------------

# Tudo o que muda entre os dashboards de turmas: modelo, formulário, textos e
# nomes das rotas (usados nos redirects e nos templates).
TURMAS_CATEQUESE = {
    'modelo': TurmaCatequeseInfantil,
    'form': TurmaForm,
    'titulo': 'Turmas Catequese',
    'subtitulo': 'Coordenação · Catequese Infantil',
    'url_dashboard': 'core:dashboard_turmas_catequese',
    'url_criar': 'core:criar_turma_catequese',
    'url_editar': 'core:editar_turma_catequese',
    'url_alternar': 'core:alternar_turma_catequese_ativa',
}

TURMAS_SEMENTINHA = {
    'modelo': TurmaSementinha,
    'form': TurmaSementinhaForm,
    'titulo': 'Turmas Sementinha',
    'subtitulo': 'Coordenação · Sementinha',
    'url_dashboard': 'core:dashboard_turmas_sementinha',
    'url_criar': 'core:criar_turma_sementinha',
    'url_editar': 'core:editar_turma_sementinha',
    'url_alternar': 'core:alternar_turma_sementinha_ativa',
}

TURMAS_CRISMA = {
    'modelo': TurmaCrisma,
    'form': TurmaCrismaForm,
    'titulo': 'Turmas Crisma',
    'subtitulo': 'Coordenação · Crisma',
    'url_dashboard': 'core:dashboard_turmas_crisma',
    'url_criar': 'core:criar_turma_crisma',
    'url_editar': 'core:editar_turma_crisma',
    'url_alternar': 'core:alternar_turma_crisma_ativa',
}

TURMAS_CATEQUESE_ADULTO = {
    'modelo': TurmaCatequeseAdulto,
    'form': TurmaCatequeseAdultoForm,
    'titulo': 'Turmas Catequese Adulto',
    'subtitulo': 'Coordenação · Catequese de Adultos',
    'url_dashboard': 'core:dashboard_turmas_catequese_adulto',
    'url_criar': 'core:criar_turma_catequese_adulto',
    'url_editar': 'core:editar_turma_catequese_adulto',
    'url_alternar': 'core:alternar_turma_catequese_adulto_ativa',
}

TURMAS_PERSEVERANCA_MEJ = {
    'modelo': TurmaPerseveranca_MEJ,
    'form': TurmaPerseveranca_MEJForm,
    'titulo': 'Turmas MEJ',
    'subtitulo': 'Coordenação · MEJ',
    'url_dashboard': 'core:dashboard_turmas_perseveranca_mej',
    'url_criar': 'core:criar_turma_perseveranca_mej',
    'url_editar': 'core:editar_turma_perseveranca_mej',
    'url_alternar': 'core:alternar_turma_perseveranca_mej_ativa',
}


def _contexto_turmas(config, **extra):
    contexto = {k: v for k, v in config.items() if k not in ('modelo', 'form')}
    contexto.update(extra)
    return contexto


def _dashboard_turmas(request, config):
    turmas = config['modelo'].objects.all()
    return render(request, 'dashboard_turmas.html', _contexto_turmas(config, turmas=turmas))


def _criar_turma(request, config):
    if request.method == 'POST':
        form = config['form'](request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Turma criada com sucesso.')
            return redirect(config['url_dashboard'])
    else:
        form = config['form']()
    return render(request, 'turma_form.html', _contexto_turmas(config, form=form, titulo='Nova turma'))


def _editar_turma(request, config, turma_id):
    turma = get_object_or_404(config['modelo'], id=turma_id)
    if request.method == 'POST':
        form = config['form'](request.POST, instance=turma)
        if form.is_valid():
            form.save()
            messages.success(request, 'Turma atualizada com sucesso.')
            return redirect(config['url_dashboard'])
    else:
        form = config['form'](instance=turma)
    return render(request, 'turma_form.html', _contexto_turmas(config, form=form, titulo=f'Editar turma: {turma.nome}'))


def _alternar_turma_ativa(request, config, turma_id):
    if request.method == 'POST':
        turma = get_object_or_404(config['modelo'], id=turma_id)
        turma.ativa = not turma.ativa
        turma.save()
    return redirect(config['url_dashboard'])


@coordenacao_required
def dashboard_turmas_catequese(request):
    return _dashboard_turmas(request, TURMAS_CATEQUESE)


@coordenacao_required
def criar_turma_catequese(request):
    return _criar_turma(request, TURMAS_CATEQUESE)


@coordenacao_required
def editar_turma_catequese(request, turma_id):
    return _editar_turma(request, TURMAS_CATEQUESE, turma_id)


@coordenacao_required
def alternar_turma_catequese_ativa(request, turma_id):
    return _alternar_turma_ativa(request, TURMAS_CATEQUESE, turma_id)


@coordenacao_required
def dashboard_turmas_sementinha(request):
    return _dashboard_turmas(request, TURMAS_SEMENTINHA)


@coordenacao_required
def criar_turma_sementinha(request):
    return _criar_turma(request, TURMAS_SEMENTINHA)


@coordenacao_required
def editar_turma_sementinha(request, turma_id):
    return _editar_turma(request, TURMAS_SEMENTINHA, turma_id)


@coordenacao_required
def alternar_turma_sementinha_ativa(request, turma_id):
    return _alternar_turma_ativa(request, TURMAS_SEMENTINHA, turma_id)


@coordenacao_required
def dashboard_turmas_crisma(request):
    return _dashboard_turmas(request, TURMAS_CRISMA)


@coordenacao_required
def criar_turma_crisma(request):
    return _criar_turma(request, TURMAS_CRISMA)


@coordenacao_required
def editar_turma_crisma(request, turma_id):
    return _editar_turma(request, TURMAS_CRISMA, turma_id)


@coordenacao_required
def alternar_turma_crisma_ativa(request, turma_id):
    return _alternar_turma_ativa(request, TURMAS_CRISMA, turma_id)


@coordenacao_required
def dashboard_turmas_catequese_adulto(request):
    return _dashboard_turmas(request, TURMAS_CATEQUESE_ADULTO)


@coordenacao_required
def criar_turma_catequese_adulto(request):
    return _criar_turma(request, TURMAS_CATEQUESE_ADULTO)


@coordenacao_required
def editar_turma_catequese_adulto(request, turma_id):
    return _editar_turma(request, TURMAS_CATEQUESE_ADULTO, turma_id)


@coordenacao_required
def alternar_turma_catequese_adulto_ativa(request, turma_id):
    return _alternar_turma_ativa(request, TURMAS_CATEQUESE_ADULTO, turma_id)


@coordenacao_required
def dashboard_turmas_perseveranca_mej(request):
    return _dashboard_turmas(request, TURMAS_PERSEVERANCA_MEJ)


@coordenacao_required
def criar_turma_perseveranca_mej(request):
    return _criar_turma(request, TURMAS_PERSEVERANCA_MEJ)


@coordenacao_required
def editar_turma_perseveranca_mej(request, turma_id):
    return _editar_turma(request, TURMAS_PERSEVERANCA_MEJ, turma_id)


@coordenacao_required
def alternar_turma_perseveranca_mej_ativa(request, turma_id):
    return _alternar_turma_ativa(request, TURMAS_PERSEVERANCA_MEJ, turma_id)


# ---------------------------------------------------------------------------
# Ajuste entre pastorais -- a coordenação transfere uma ficha feita no
# formulário errado (ex.: Crisma -> Sementinha)
# ---------------------------------------------------------------------------

@coordenacao_required
def ajuste_pastorais(request):
    origem = request.GET.get('pastoral', 'crisma')
    if origem not in PASTORAIS_AJUSTE:
        origem = 'crisma'
    busca = request.GET.get('busca', '').strip()
    fichas = PASTORAIS_AJUSTE[origem]['modelo'].objects.select_related('turma').order_by('nome')
    if busca:
        fichas = fichas.filter(nome__icontains=busca)
    contexto = {
        'pastorais': PASTORAIS_AJUSTE,
        'origem': origem,
        'titulo_origem': PASTORAIS_AJUSTE[origem]['titulo'],
        'busca': busca,
        'fichas': fichas,
    }
    return render(request, 'ajuste_pastorais.html', contexto)


@coordenacao_required
def transferir_ficha_pastoral(request, origem, ficha_id, destino=None):
    if origem not in PASTORAIS_AJUSTE:
        raise Http404
    ficha = get_object_or_404(PASTORAIS_AJUSTE[origem]['modelo'], id=ficha_id)
    destinos = {chave: p for chave, p in PASTORAIS_AJUSTE.items() if chave != origem}
    contexto = {
        'ficha': ficha,
        'origem': origem,
        'titulo_origem': PASTORAIS_AJUSTE[origem]['titulo'],
        'destinos': destinos,
        'destino': destino,
    }
    if destino is None:
        return render(request, 'ajuste_pastoral_transferir.html', contexto)
    if destino not in destinos:
        raise Http404

    config = destinos[destino]
    kwargs = dict(turma_model=config['turma'], ficha=ficha, exige_responsavel=config['exige_responsavel'])
    if request.method == 'POST':
        form = AjustePastoralForm(request.POST, **kwargs)
        if form.is_valid():
            dados = {nome: form.cleaned_data[nome] for nome in CAMPOS_RESPONSAVEL if nome in form.cleaned_data}
            id_origem = ficha.pk
            with transaction.atomic():
                nova = transferir_ficha(ficha, config['modelo'], form.cleaned_data['turma'], **dados)
                registrar_log(
                    LogFicha.TRANSFERENCIA, nova, request.user,
                    detalhe=f"De {contexto['titulo_origem']} (ficha nº {id_origem}) para {config['titulo']}",
                )
            messages.success(
                request,
                f"Ficha de {nova.nome} transferida de {contexto['titulo_origem']} para {config['titulo']}.",
            )
            return redirect(f"{resolve_url('core:ajuste_pastorais')}?pastoral={destino}")
    else:
        form = AjustePastoralForm(**kwargs)

    contexto.update(
        form=form,
        titulo_destino=config['titulo'],
        perdidos=campos_perdidos(ficha, config['modelo']),
    )
    return render(request, 'ajuste_pastoral_transferir.html', contexto)


# ---------------------------------------------------------------------------
# Logs -- a coordenação consulta o histórico de ações sobre as fichas
# (somente leitura: não há edição nem remoção de registros pela tela)
# ---------------------------------------------------------------------------

LOGS_POR_PAGINA = 50


@coordenacao_required
def logs_fichas(request):
    filtros = {
        'acao': request.GET.get('acao', ''),
        'pastoral': request.GET.get('pastoral', ''),
        'usuario': request.GET.get('usuario', ''),
        'de': request.GET.get('de', ''),
        'ate': request.GET.get('ate', ''),
        'busca': request.GET.get('busca', '').strip(),
    }
    logs = LogFicha.objects.all()
    if filtros['acao'] in dict(LogFicha.ACOES):
        logs = logs.filter(acao=filtros['acao'])
    if filtros['pastoral'] in dict(LogFicha.PASTORAIS):
        logs = logs.filter(pastoral=filtros['pastoral'])
    if filtros['usuario']:
        logs = logs.filter(usuario_nome=filtros['usuario'])
    if filtros['busca']:
        logs = logs.filter(nome_ficha__icontains=filtros['busca'])
    try:
        if filtros['de']:
            logs = logs.filter(criado_em__date__gte=date.fromisoformat(filtros['de']))
        if filtros['ate']:
            logs = logs.filter(criado_em__date__lte=date.fromisoformat(filtros['ate']))
    except ValueError:
        messages.error(request, 'Data inválida no filtro de período.')

    pagina = Paginator(logs, LOGS_POR_PAGINA).get_page(request.GET.get('pagina'))
    # Mantém os filtros ao trocar de página
    parametros = request.GET.copy()
    parametros.pop('pagina', None)

    contexto = {
        'pagina': pagina,
        'filtros': filtros,
        'filtrando': any(filtros.values()),
        'acoes': LogFicha.ACOES,
        'pastorais': LogFicha.PASTORAIS,
        'usuarios': LogFicha.objects.order_by('usuario_nome')
                                    .values_list('usuario_nome', flat=True).distinct(),
        'querystring': parametros.urlencode(),
    }
    return render(request, 'logs_fichas.html', contexto)
