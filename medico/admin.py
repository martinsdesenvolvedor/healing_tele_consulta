from django.contrib import admin
from .models import Especialidades, DadosMedico, DatasAbertas

# Register your models here.
class DataAbertasAdmin(admin.ModelAdmin):
    list_display = ('data', 'user', 'agendado')

admin.site.register(Especialidades)
admin.site.register(DadosMedico)
admin.site.register(DatasAbertas, DataAbertasAdmin)