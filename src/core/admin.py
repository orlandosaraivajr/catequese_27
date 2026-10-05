from django.contrib import admin
from core.models import CatequeseAdultoModel
from core.models import CatequeseInfantilModel
from core.models import CrismaModel
from core.models import Perseveranca_MEJ_Model
from core.models import NoivoModel
from core.models import CoroinhaModel
from core.models import TurmaCatequeseInfantil


class TurmaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ativa', 'vagas_maximas', 'vagas_ocupadas', 'idade_minima', 'idade_maxima', 'ordem')
    list_editable = ('ativa', 'ordem')
    search_fields = ('nome',)

    @admin.display(description='Vagas ocupadas')
    def vagas_ocupadas(self, obj):
        return obj.vagas_ocupadas


class CatequeseInfantilAdmin(admin.ModelAdmin):
    list_display = ('nome','turma','data_nascimento','criado_em')
    list_filter = ('turma',)
    date_hierarchy = 'criado_em'
    search_fields = ('nome','data_nascimento','criado_em')

class CatequeseAdultoAdmin(admin.ModelAdmin):
    list_display = ('nome','data_nascimento','criado_em')
    date_hierarchy = 'criado_em'
    search_fields = ('nome','data_nascimento','criado_em')

class CrismaAdmin(admin.ModelAdmin):
    list_display = ('nome','data_nascimento','criado_em')
    date_hierarchy = 'criado_em'
    search_fields = ('nome','data_nascimento','criado_em')

class Perseveranca_MEJ_Admin(admin.ModelAdmin):
    list_display = ('nome','data_nascimento','criado_em')
    date_hierarchy = 'criado_em'
    search_fields = ('nome','data_nascimento','criado_em')

class NoivoAdmin(admin.ModelAdmin):
    list_display = ('nome_noivo','nome_noiva','data_provavel_casamento','criado_em')
    date_hierarchy = 'criado_em'
    search_fields = ('nome_noivo','nome_noiva','data_provavel_casamento','criado_em')
class CoroinhaAdmin(admin.ModelAdmin):
    list_display = ('nome','data_nascimento','criado_em')
    date_hierarchy = 'criado_em'
    search_fields = ('nome','data_nascimento','criado_em')
        
admin.site.register(TurmaCatequeseInfantil, TurmaAdmin)
admin.site.register(CatequeseInfantilModel, CatequeseInfantilAdmin)
admin.site.register(CatequeseAdultoModel, CatequeseAdultoAdmin)
admin.site.register(CrismaModel, CrismaAdmin)
admin.site.register(Perseveranca_MEJ_Model, Perseveranca_MEJ_Admin)
admin.site.register(NoivoModel, NoivoAdmin)
admin.site.register(CoroinhaModel, CoroinhaAdmin)