from django.forms import ModelForm
from .models import Evento, Asistente, Registro,Task
from django import forms

class taskForm(ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'important', 'datecompleted']

class EventForm(ModelForm):
    class Meta:
        model = Evento
        fields = ['nombre', 'fecha']

class AsistenteForm(ModelForm):
    class Meta:
        model = Asistente
        fields = ['evento', 'nombre']

class RegistroForm(ModelForm):
    class Meta:
        model = Registro

        # Solo pedimos los datos que el usuario debe seleccionar.
        # MODIFICADO: Ya no necesitamos pedir el evento, se obtiene del asistente.
        fields = ['asistente', 'check_in', 'check_out']
        widgets = {
            'asistente': forms.Select(attrs={'class': 'form-control'}),
        }