from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.timezone import localtime
from django.http import HttpResponse, FileResponse
from django.db.models import Count
from .forms import CatequeseInfantilForm, CrismaForm, PerseverancaMejForm, CatequeseAdultoForm, NoivoForm, CoroinhaForm, TurmaForm
from .models import CatequeseInfantilModel, CrismaModel, Perseveranca_MEJ_Model, CatequeseAdultoModel, NoivoModel, CoroinhaModel, Turma
from .services import gerar_ficha_catequese, gerar_ficha_crisma, gerar_ficha_perseveranca_mej
from .services import gerar_ficha_catequese_adulto, gerar_ficha_noivos ,  gerar_Workbook, gerar_ficha_coroinhas


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

@login_required
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
        .values('horario')
        .annotate(quantidade=Count('id'))
        .order_by('-quantidade')
    )
    horarios_dict = dict(CrismaModel.HORARIO_CRISMA)
    total_crisma = [
        {
            "titulo": horarios_dict.get(item["horario"]),
            "quantidade": item["quantidade"]
        }
        for item in qs
    ]
    # Perseverança / MEJ
    qs = (
        Perseveranca_MEJ_Model.objects
        .values('horario')
        .annotate(quantidade=Count('id'))
        .order_by('-quantidade')
    )
    horarios_dict = dict(Perseveranca_MEJ_Model.HORARIO_PERSEVERANCA)
    total_perseveranca_mej = [
        {
            "titulo": horarios_dict.get(item["horario"]),
            "quantidade": item["quantidade"]
        }
        for item in qs
    ]
    # Catequese Adulto
    qs = (
        CatequeseAdultoModel.objects
        .values('horario')
        .annotate(quantidade=Count('id'))
        .order_by('-quantidade')
    )
    horarios_dict = dict(CatequeseAdultoModel.HORARIO_CATEQUESE_ADULTO)
    total_catequese_adulto = [
        {
            "titulo": horarios_dict.get(item["horario"]),
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

@login_required
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
# Dashboard da coordenação -- turmas da Catequese Infantil
# ---------------------------------------------------------------------------

@staff_member_required
def dashboard_turmas(request):
    turmas = Turma.objects.all()
    return render(request, 'dashboard_turmas.html', {'turmas': turmas})


@staff_member_required
def criar_turma(request):
    if request.method == 'POST':
        form = TurmaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Turma criada com sucesso.')
            return redirect('core:dashboard_turmas')
    else:
        form = TurmaForm()
    return render(request, 'turma_form.html', {'form': form, 'titulo': 'Nova turma'})


@staff_member_required
def editar_turma(request, turma_id):
    turma = get_object_or_404(Turma, id=turma_id)
    if request.method == 'POST':
        form = TurmaForm(request.POST, instance=turma)
        if form.is_valid():
            form.save()
            messages.success(request, 'Turma atualizada com sucesso.')
            return redirect('core:dashboard_turmas')
    else:
        form = TurmaForm(instance=turma)
    return render(request, 'turma_form.html', {'form': form, 'titulo': f'Editar turma: {turma.nome}'})


@staff_member_required
def alternar_turma_ativa(request, turma_id):
    if request.method == 'POST':
        turma = get_object_or_404(Turma, id=turma_id)
        turma.ativa = not turma.ativa
        turma.save()
    return redirect('core:dashboard_turmas')