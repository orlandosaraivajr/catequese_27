from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.utils.timezone import localtime
from django.http import HttpResponse, FileResponse
from django.db.models import Count
from .forms import CatequeseInfantilForm, CrismaForm, PerseverancaMejForm, CatequeseAdultoForm, NoivoForm, CoroinhaForm, TurmaForm, TurmaCrismaForm, TurmaCatequeseAdultoForm, TurmaPerseveranca_MEJForm, CoordenacaoLoginForm
from .models import CatequeseInfantilModel, CrismaModel, Perseveranca_MEJ_Model, CatequeseAdultoModel, NoivoModel, CoroinhaModel, TurmaCatequeseInfantil, TurmaCrisma, TurmaCatequeseAdulto, TurmaPerseveranca_MEJ
from .services import gerar_ficha_catequese, gerar_ficha_crisma, gerar_ficha_perseveranca_mej
from .services import gerar_ficha_catequese_adulto, gerar_ficha_noivos ,  gerar_Workbook, gerar_ficha_coroinhas

# Views da coordenação redirecionam para o login próprio, e não para o admin
coordenacao_required = staff_member_required(login_url='core:coordenacao')


def index(request):
    return render(request, 'index.html')

def catequese_infantil(request):
    if request.method == 'POST':
        form = CatequeseInfantilForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('core:procure_secretaria')
    else:
        form = CatequeseInfantilForm()
    return render(request, 'catequese_infantil.html', {'form': form})

@coordenacao_required
def crisma(request):
    if request.method == 'POST':
        form = CrismaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('core:procure_secretaria')
    else:
        form = CrismaForm()
    return render(request, 'crisma.html', {'form': form})

def perseveranca_mej(request):
    if request.method == 'POST':
        form = PerseverancaMejForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('core:procure_secretaria')
    else:
        form = PerseverancaMejForm()
    return render(request, 'perseveranca.html', {'form': form})

def catequese_adulto(request):
    if request.method == 'POST':
        form = CatequeseAdultoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('core:procure_secretaria')
    else:
        form = CatequeseAdultoForm()
    return render(request, 'catequese_adulto.html', {'form': form})

def noivos(request):
    if request.method == 'POST':
        form = NoivoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('core:procure_secretaria')
    else:
        form = NoivoForm()
    return render(request, 'noivos.html', {'form': form})

def coroinhas(request):
    if request.method == 'POST':
        form = CoroinhaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('core:procure_secretaria')
    else:
        form = CoroinhaForm()
    return render(request, 'coroinhas.html', {'form': form})

def procure_secretaria(request):
    return render(request, 'procure_secretaria.html')

def listar_fichas(request):
    fichas = CatequeseInfantilModel.objects.filter(ficha_impressa=False).filter(ficha_assinada=False).order_by('nome')
    fichasCrisma = CrismaModel.objects.filter(ficha_impressa=False).filter(ficha_assinada=False).order_by('nome')
    fichasMEJ = Perseveranca_MEJ_Model.objects.filter(ficha_impressa=False).filter(ficha_assinada=False).order_by('nome')
    fichasAdultos = CatequeseAdultoModel.objects.filter(ficha_impressa=False).filter(ficha_assinada=False).order_by('nome')
    fichasNoivos = NoivoModel.objects.filter(ficha_impressa=False).filter(ficha_assinada=False).order_by('nome_noivo')
    fichasCoroinhas = CoroinhaModel.objects.filter(ficha_impressa=False).filter(ficha_assinada=False).order_by('nome')
    mensagem = 'Fichas Pendentes de Impressão'
    contexto = {'fichas': fichas,'fichasCrisma': fichasCrisma, 
                'fichasMEJ': fichasMEJ,'fichasAdultos': fichasAdultos,
                'fichasNoivos': fichasNoivos,
                'fichasCoroinhas': fichasCoroinhas,
                'mensagem': mensagem}
    return render(request, 'listar_fichas.html', contexto)

def listar_todas_fichas(request):
    fichas = CatequeseInfantilModel.objects.all().filter(ficha_assinada=False).order_by('nome')
    fichasCrisma = CrismaModel.objects.all().filter(ficha_assinada=False).order_by('nome')
    fichasMEJ = Perseveranca_MEJ_Model.objects.all().filter(ficha_assinada=False).order_by('nome')
    fichasAdultos = CatequeseAdultoModel.objects.all().filter(ficha_assinada=False).order_by('nome')
    fichasNoivos = NoivoModel.objects.all().filter(ficha_assinada=False).order_by('nome_noivo')
    fichasCoroinhas = CoroinhaModel.objects.all().filter(ficha_assinada=False).order_by('nome')
    mensagem = 'Fichas Pendentes de Impressão'
    contexto = {'fichas': fichas,'fichasCrisma': fichasCrisma, 
                'fichasMEJ': fichasMEJ,'fichasAdultos': fichasAdultos,
                'fichasNoivos': fichasNoivos,
                'fichasCoroinhas': fichasCoroinhas,
                'mensagem': mensagem}
    return render(request, 'listar_fichas.html', contexto)

def imprimir_ficha(request):
    if request.method == 'POST':
        ficha_id = request.POST.get('ficha_id')
        ficha = get_object_or_404(CatequeseInfantilModel, id=ficha_id)
        ficha.ficha_impressa = True
        ficha.save()
        pdf_path = gerar_ficha_catequese(ficha)
        return FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')
    return redirect('core:listar_fichas')

def assinar_ficha(request):
    if request.method == 'POST':
        ficha_id = request.POST.get('ficha_id')
        ficha = get_object_or_404(CatequeseInfantilModel, id=ficha_id)
        ficha.ficha_assinada = True
        ficha.save()
    return redirect('core:listar_fichas')

def remover_ficha(request):
    if request.method == 'POST':
        ficha_id = request.POST.get('ficha_id')
        ficha = get_object_or_404(CatequeseInfantilModel, id=ficha_id)
        ficha.delete()
    return redirect('core:listar_fichas')

def imprimir_ficha_crisma(request):
    if request.method == 'POST':
        ficha_id = request.POST.get('ficha_id')
        ficha = get_object_or_404(CrismaModel, id=ficha_id)
        ficha.ficha_impressa = True
        ficha.save()
        pdf_path = gerar_ficha_crisma(ficha)
        return FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')
    return redirect('core:listar_fichas')

def assinar_ficha_crisma(request):
    if request.method == 'POST':
        ficha_id = request.POST.get('ficha_id')
        ficha = get_object_or_404(CrismaModel, id=ficha_id)
        ficha.ficha_assinada = True
        ficha.save()
    return redirect('core:listar_fichas')

def remover_ficha_crisma(request):
    if request.method == 'POST':
        ficha_id = request.POST.get('ficha_id')
        ficha = get_object_or_404(CrismaModel, id=ficha_id)
        ficha.delete()
    return redirect('core:listar_fichas')

def imprimir_ficha_perseveranca_mej(request):
    if request.method == 'POST':
        ficha_id = request.POST.get('ficha_id')
        ficha = get_object_or_404(Perseveranca_MEJ_Model, id=ficha_id)
        ficha.ficha_impressa = True
        ficha.save()
        pdf_path = gerar_ficha_perseveranca_mej(ficha)
        return FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')
    return redirect('core:listar_fichas')

def assinar_ficha_perseveranca_mej(request):
    if request.method == 'POST':
        ficha_id = request.POST.get('ficha_id')
        ficha = get_object_or_404(Perseveranca_MEJ_Model, id=ficha_id)
        ficha.ficha_assinada = True
        ficha.save()
    return redirect('core:listar_fichas')

def remover_ficha_perseveranca_mej(request):
    if request.method == 'POST':
        ficha_id = request.POST.get('ficha_id')
        ficha = get_object_or_404(Perseveranca_MEJ_Model, id=ficha_id)
        ficha.delete()
    return redirect('core:listar_fichas')

def imprimir_ficha_adulto(request):
    if request.method == 'POST':
        ficha_id = request.POST.get('ficha_id')
        ficha = get_object_or_404(CatequeseAdultoModel, id=ficha_id)
        ficha.ficha_impressa = True
        ficha.save()
        pdf_path = gerar_ficha_catequese_adulto(ficha)
        return FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')
    return redirect('core:listar_fichas')

def assinar_ficha_adulto(request):
    if request.method == 'POST':
        ficha_id = request.POST.get('ficha_id')
        ficha = get_object_or_404(CatequeseAdultoModel, id=ficha_id)
        ficha.ficha_assinada = True
        ficha.save()
    return redirect('core:listar_fichas')

def remover_ficha_adulto(request):
    if request.method == 'POST':
        ficha_id = request.POST.get('ficha_id')
        ficha = get_object_or_404(CatequeseAdultoModel, id=ficha_id)
        ficha.delete()
    return redirect('core:listar_fichas')

def imprimir_ficha_noivos(request):
    if request.method == 'POST':
        ficha_id = request.POST.get('ficha_id')
        ficha = get_object_or_404(NoivoModel, id=ficha_id)
        ficha.ficha_impressa = True
        ficha.save()
        pdf_path = gerar_ficha_noivos(ficha)
        return FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')
    return redirect('core:listar_fichas')

def assinar_ficha_noivos(request):
    if request.method == 'POST':
        ficha_id = request.POST.get('ficha_id')
        ficha = get_object_or_404(NoivoModel, id=ficha_id)
        ficha.ficha_assinada = True
        ficha.save()
    return redirect('core:listar_fichas')

def remover_ficha_noivos(request):
    if request.method == 'POST':
        ficha_id = request.POST.get('ficha_id')
        ficha = get_object_or_404(NoivoModel, id=ficha_id)
        ficha.delete()
    return redirect('core:listar_fichas')

def imprimir_ficha_coroinhas(request):
    if request.method == 'POST':
        ficha_id = request.POST.get('ficha_id')
        ficha = get_object_or_404(CoroinhaModel, id=ficha_id)
        ficha.ficha_impressa = True
        ficha.save()
        pdf_path = gerar_ficha_coroinhas(ficha)
        return FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')
    return redirect('core:listar_fichas')

def assinar_ficha_coroinhas(request):
    if request.method == 'POST':
        ficha_id = request.POST.get('ficha_id')
        ficha = get_object_or_404(CoroinhaModel, id=ficha_id)
        ficha.ficha_assinada = True
        ficha.save()
    return redirect('core:listar_fichas')

def remover_ficha_coroinhas(request):
    if request.method == 'POST':
        ficha_id = request.POST.get('ficha_id')
        ficha = get_object_or_404(CoroinhaModel, id=ficha_id)
        ficha.delete()
    return redirect('core:listar_fichas')

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
        'total_crisma': total_crisma,
        'total_perseveranca_mej': total_perseveranca_mej,
        'total_catequese_adulto': total_catequese_adulto,
    }
    return render(request, 'contador_fichas.html', contexto)

@coordenacao_required
def exportar_excel(request):
    wb = gerar_Workbook()
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    file_name = 'relatorio_catequese_' + localtime().strftime('%d_%m_%Y__%Hh_%Mm')
    response['Content-Disposition'] = 'attachment; filename=' + file_name + '.xlsx'
    wb.save(response)
    return response


# ---------------------------------------------------------------------------
# Login / logout da coordenação
# ---------------------------------------------------------------------------

class CoordenacaoLoginView(LoginView):
    template_name = 'coordenacao_login.html'
    authentication_form = CoordenacaoLoginForm

    def dispatch(self, request, *args, **kwargs):
        # Coordenadora já logada vai direto para a dashboard.
        # (Usuário comum logado vê o formulário, evitando loop de redirect.)
        if request.user.is_authenticated and request.user.is_staff:
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)


def coordenacao_logout(request):
    if request.method != 'POST':
        # GET não desloga (evita logout forçado via link/imagem de outro site);
        # apenas leva de volta à área da coordenação.
        return redirect('core:coordenacao')
    logout(request)
    messages.info(request, 'Você saiu da área da coordenação.')
    return redirect('core:coordenacao')


# ---------------------------------------------------------------------------
# Dashboard da coordenação -- turmas da Catequese Infantil, Crisma, Catequese de Adultos
# e Perseverança / MEJ
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
