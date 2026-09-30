from django.shortcuts import redirect

def index(request):
    return redirect('core:index')

def secretaria(request):
    return redirect('core:secretaria')

def excel(request):
    return redirect('core:exportar-excel')

def total(request):
    return redirect('core:total')