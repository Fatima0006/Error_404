from django.contrib import admin
from .models import Task, Evento, Asistente

class TaskAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'updated')
     
# Register your models here.
admin.site.register(Task, TaskAdmin)
admin.site.register(Evento)
admin.site.register(Asistente)
# Almacena la relación entre asistentes y eventos, incluyendo la fecha de registro.
