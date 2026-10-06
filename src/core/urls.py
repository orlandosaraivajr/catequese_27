from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('catequese_infantil', views.catequese_infantil, name='catequese_infantil'),
    path('crisma', views.crisma, name='crisma'),
    path('perseveranca', views.perseveranca_mej, name='perseveranca_mej'),
    path('catequese_adulto', views.catequese_adulto, name='catequese_adulto'),
    path('procure-secretaria', views.procure_secretaria, name='procure_secretaria'),
    path('noivos', views.noivos, name='noivos'),
    path('coroinhas', views.coroinhas, name='coroinhas'),
    # Secretaria
    path('secretaria', views.listar_fichas, name='secretaria'),
    path('listar-fichas/', views.listar_fichas, name='listar_fichas'),
    path('listar-todas-fichas/', views.listar_todas_fichas, name='listar_todas_fichas'),
    # Catequese Infantil
    path('imprimir-ficha', views.imprimir_ficha, name='imprimir_ficha'),
    path('assinar-ficha', views.assinar_ficha, name='assinar_ficha'),
    path('remover-ficha', views.remover_ficha, name='remover_ficha'),
    # Crisma
    path('imprimir-ficha-crisma', views.imprimir_ficha_crisma, name='imprimir_ficha_crisma'),
    path('assinar-ficha-crisma', views.assinar_ficha_crisma, name='assinar_ficha_crisma'),
    path('remover-ficha-crisma', views.remover_ficha_crisma, name='remover_ficha_crisma'),
    # Perseverança
    path('imprimir-ficha-perseveranca-mej', views.imprimir_ficha_perseveranca_mej, name='imprimir_ficha_perseveranca_mej'),
    path('assinar-ficha-perseveranca-mej', views.assinar_ficha_perseveranca_mej, name='assinar_ficha_perseveranca_mej'),
    path('remover-ficha-perseveranca-mej', views.remover_ficha_perseveranca_mej, name='remover_ficha_perseveranca_mej'),
    # Catequese Adulto
    path('imprimir-ficha-adulto', views.imprimir_ficha_adulto, name='imprimir_ficha_adulto'),
    path('assinar-ficha-adulto', views.assinar_ficha_adulto, name='assinar_ficha_adulto'),
    path('remover-ficha-adulto', views.remover_ficha_adulto, name='remover_ficha_adulto'),
    # Noivos
    path('imprimir-ficha-noivos', views.imprimir_ficha_noivos, name='imprimir_ficha_noivos'),
    path('assinar-ficha-noivos', views.assinar_ficha_noivos, name='assinar_ficha_noivos'),
    path('remover-ficha-noivos', views.remover_ficha_noivos, name='remover_ficha_noivos'),
    # Coroinhas
    path('imprimir-ficha-coroinhas', views.imprimir_ficha_coroinhas, name='imprimir_ficha_coroinhas'),
    path('assinar-ficha-coroinhas', views.assinar_ficha_coroinhas, name='assinar_ficha_coroinhas'),
    path('remover-ficha-coroinhas', views.remover_ficha_coroinhas, name='remover_ficha_coroinhas'),
    # Exportar Excel
    path('total', views.total, name='total'),
    path('excel', views.exportar_excel, name='exportar-excel'),
    # Login / logout da coordenação
    path('coordenacao', views.CoordenacaoLoginView.as_view(), name='coordenacao'),
    path('coordenacao/sair', views.coordenacao_logout, name='coordenacao_logout'),
    # Dashboard da coordenação -- turmas da Catequese Infantil
    path('coordenacao/turmas_catequese', views.dashboard_turmas_catequese, name='dashboard_turmas_catequese'),
    path('coordenacao/turmas_catequese/nova', views.criar_turma_catequese, name='criar_turma_catequese'),
    path('coordenacao/turmas_catequese/<int:turma_id>/editar', views.editar_turma_catequese, name='editar_turma_catequese'),
    path('coordenacao/turmas_catequese/<int:turma_id>/alternar', views.alternar_turma_catequese_ativa, name='alternar_turma_catequese_ativa'),

    # Dashboard da coordenação -- turmas da Crisma
    path('coordenacao/turmas_crisma', views.dashboard_turmas_crisma, name='dashboard_turmas_crisma'),
    path('coordenacao/turmas_crisma/nova', views.criar_turma_crisma, name='criar_turma_crisma'),
    path('coordenacao/turmas_crisma/<int:turma_id>/editar', views.editar_turma_crisma, name='editar_turma_crisma'),
    path('coordenacao/turmas_crisma/<int:turma_id>/alternar', views.alternar_turma_crisma_ativa, name='alternar_turma_crisma_ativa'),

    # Dashboard da coordenação -- turmas da Catequese de Adultos
    path('coordenacao/turmas_catequese_adulto', views.dashboard_turmas_catequese_adulto, name='dashboard_turmas_catequese_adulto'),
    path('coordenacao/turmas_catequese_adulto/nova', views.criar_turma_catequese_adulto, name='criar_turma_catequese_adulto'),
    path('coordenacao/turmas_catequese_adulto/<int:turma_id>/editar', views.editar_turma_catequese_adulto, name='editar_turma_catequese_adulto'),
    path('coordenacao/turmas_catequese_adulto/<int:turma_id>/alternar', views.alternar_turma_catequese_adulto_ativa, name='alternar_turma_catequese_adulto_ativa'),
]