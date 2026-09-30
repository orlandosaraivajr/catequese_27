from django.urls import path
from . import views

app_name = 'index'

urlpatterns = [
    path('', views.index, name='index'),
    path('secretaria', views.secretaria, name='secretaria'),
    path('excel', views.excel, name='excel'),
    path('total', views.total, name='total'),
]