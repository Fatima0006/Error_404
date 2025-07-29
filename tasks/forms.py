from django.forms import ModelForm
from .models import Evento, Asistente, Registro,Task

class taskForm(ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'important']