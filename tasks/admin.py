from django.contrib import admin
from .models import Task, Evento, Asistente

# Register your models here.
admin.site.register(Task)
admin.site.register(Evento)
admin.site.register(Asistente)
# Almacena la relación entre asistentes y eventos, incluyendo la fecha de registro.
