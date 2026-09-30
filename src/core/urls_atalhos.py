from django.urls import path
from django.views.generic import RedirectView

# Atalhos na raiz do site que redirecionam para as rotas do app core.
urlpatterns = [
    path('', RedirectView.as_view(pattern_name='core:index'), name='atalho_index'),
    path('secretaria', RedirectView.as_view(pattern_name='core:secretaria'), name='atalho_secretaria'),
    path('excel', RedirectView.as_view(pattern_name='core:exportar-excel'), name='atalho_excel'),
    path('total', RedirectView.as_view(pattern_name='core:total'), name='atalho_total'),
]
