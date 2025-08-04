from django.forms import ModelForm
from .models import Evento, Asistente, Registro,Task

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
        fields = ['nombre']

class RegistroForm(ModelForm):
    class Meta:
        model = Registro 
        # Solo pedimos los datos que el usuario debe seleccionar.
        # 'check_in' y 'check_out' se manejarán en la vista.
        fields = ['evento', 'asistente']
        widgets = {
            'evento': forms.Select(attrs={'class': 'form-control'}),
            'asistente': forms.Select(attrs={'class': 'form-control'}),
        }