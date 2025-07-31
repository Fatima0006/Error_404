from django.contrib import admin
from .models import Task, Evento, Asistente, Registro

class TaskAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'updated')
     
# Register your models here.
admin.site.register(Task, TaskAdmin)
# Almacena la relación entre asistentes y eventos, incluyendo la fecha de registro.

@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha')
    search_fields = ('nombre',)

@admin.register(Asistente)
class AsistenteAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(Registro)
class RegistroAdmin(admin.ModelAdmin):
    list_display = ('evento', 'asistente', 'check_in', 'check_out', 'duracion')
    list_filter = ('evento', 'check_in', 'check_out')