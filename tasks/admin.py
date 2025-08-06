from django.contrib import admin
from .models import Task, Evento, Asistente, Registro

class TaskAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'updated')
     
# Register your models here.
admin.site.register(Task, TaskAdmin)
# Almacena la relación entre asistentes y eventos, incluyendo la fecha de registro.

class AsistenteInline(admin.TabularInline):
    """Permite editar asistentes directamente desde la página del evento."""
    model = Asistente
    extra = 1  # Muestra un campo vacío para añadir un nuevo asistente.

@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha', 'user')
    search_fields = ('nombre', 'user__username')
    list_filter = ('fecha', 'user')
    inlines = [AsistenteInline]

@admin.register(Asistente)
class AsistenteAdmin(admin.ModelAdmin):
    # Mostramos el evento y permitimos filtrar y buscar por él.
    list_display = ('nombre', 'evento')
    search_fields = ('nombre', 'evento__nombre')
    list_filter = ('evento',)

@admin.register(Registro)
class RegistroAdmin(admin.ModelAdmin):
    list_display = ('evento', 'asistente', 'check_in', 'check_out', 'duracion')
    # El filtro ahora debe seguir la relación a través del asistente.
    list_filter = ('asistente__evento', 'check_in', 'check_out')