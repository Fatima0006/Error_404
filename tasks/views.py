from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import taskForm, EventForm, AsistenteForm, KioscoAsistenciaForm
from .models import Task, Registro, Evento, Asistente
from django.utils import timezone
# Aqui va a ser necesario importar el modelo EventForm
from django.http import HttpResponse

# Create your views here.


def home(request):
    return render(request, 'home.html')


def signup(request):
    if request.method == 'GET':
        form = UserCreationForm()
        return render(request, 'signup.html', {"form": form})
    else: # POST
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('tasks')
        else:
            # El formulario ya contiene los errores, solo hay que volver a mostrarlo
            return render(request, 'signup.html', {"form": form})

def eventos(request):
    eventos_list = Evento.objects.filter(user=request.user)
    return render(request, 'eventos.html', {"eventos": eventos_list})


def tasks(request):
    tasks = Task.objects.filter(user=request.user)
    return render(request, 'tasks.html', {"tasks": tasks})
def create_task(request):
    if request.method == 'POST':
        form = taskForm(request.POST)
        if form.is_valid():
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            return redirect('tasks')
    else: # GET
        form = taskForm()
    return render(request, 'create_task.html', {"form": form})
        
def task_detail(request, task_id):
    if request.method == 'GET':
        tasks = get_object_or_404(Task,pk=task_id)
        form = taskForm(instance=tasks)
        return render(request, 'task_detail.html',{"tasks":tasks,"form":form})
    else : 
        tasks = get_object_or_404(Task,pk=task_id)
        form = taskForm(request.POST, instance=tasks)
        form.save()
        return redirect('tasks')
    
def  complete_task(request, task_id):   
    task = get_object_or_404(Task, pk=task_id)
    task.datecompleted = timezone.now()
    task.save()
    return redirect('tasks')
 # -------------Checar esta parte para ver como es que funcionaria BD


from django.forms import modelformset_factory

def evento_detail(request, evento_id):
    evento = get_object_or_404(Evento, pk=evento_id)
    
    # 1. Crear el Formset para los Asistentes
    AsistenteFormSet = modelformset_factory(Asistente, form=AsistenteForm, extra=0, can_delete=True)

    if request.method == 'POST':
        # 2. Procesar ambos formularios
        form = EventForm(request.POST, instance=evento, prefix='evento')
        formset = AsistenteFormSet(request.POST, queryset=evento.asistentes.all(), prefix='asistentes')
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('evento_detail', evento_id=evento.id)

    else: # GET
        # 3. Mostrar ambos formularios
        form = EventForm(instance=evento, prefix='evento')
        formset = AsistenteFormSet(queryset=evento.asistentes.all(), prefix='asistentes')

    context = {
        'evento': evento,
        'form': form,
        'formset': formset,
    }
    return render(request, 'evento_detail.html', context)

def kiosco_asistencia(request, evento_id):
    evento = get_object_or_404(Evento, pk=evento_id)
    
    if request.method == 'POST':
        form = KioscoAsistenciaForm(request.POST, evento=evento)
        if form.is_valid():
            asistente_seleccionado = form.cleaned_data['asistente']
            
            # 1. Buscar si hay un registro (check-in o check-out) para este asistente EN ESTE evento
            registro_existente = Registro.objects.filter(
                asistente=asistente_seleccionado,
                asistente__evento=evento 
            ).first()

            if registro_existente:
                # Si ya existe un registro, verificamos si está abierto o cerrado
                if registro_existente.check_out is None:
                    # Si está abierto (solo check-in), lo cerramos (hacemos check-out)
                    registro_existente.check_out = timezone.now()
                    registro_existente.save()
                else:
                    # Si ya tiene check-out, significa que ya completó su asistencia.
                    # Opcional: Puedes mostrar un mensaje de error o simplemente no hacer nada.
                    # Por ahora, no haremos nada para evitar registros duplicados.
                    pass # El asistente ya ha sido registrado y ha salido.
            else:
                # 3. Si no existe ningún registro para este asistente en este evento, creamos uno nuevo (hacemos check-in)
                Registro.objects.create(
                    asistente=asistente_seleccionado,
                    check_in=timezone.now()
                )
            # Redirigimos a la misma página para ver el resultado
            return redirect('kiosco_asistencia', evento_id=evento.id)
    else: # GET
        form = KioscoAsistenciaForm(evento=evento)

    # 4. Preparamos la información para la tabla de estado
    asistentes_con_estado = []
    for asistente in evento.asistentes.all():
        ultimo_registro = Registro.objects.filter(asistente=asistente).order_by('-check_in').first()
        asistentes_con_estado.append({
            'asistente': asistente,
            'registro': ultimo_registro
        })

    context = {
        'evento': evento,
        'form': form,
        'asistentes_con_estado': asistentes_con_estado
    }
    return render(request, 'registrar_asistente.html', context)
        
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            new_event = form.save(commit=False)
            new_event.user = request.user
            new_event.save()
            return redirect('eventos')
    else: # GET
        form = EventForm()
    return render(request, 'create_event.html', {"form": form})

def crear_asistente(request):
    if request.method == 'POST':
        form = AsistenteForm(request.POST)
        if form.is_valid():
            try:
                # La línea `new_asistente.user = request.user` se elimina
                # porque el modelo Asistente no tiene un campo `user`.
                # La relación con el usuario está en el Evento.
                form.save()
                # Redirigimos a la misma página para que pueda añadir otro asistente.
                return redirect('crear_asistente')
            except IntegrityError:
                # Si se produce un IntegrityError, es por la restricción `unique_together`.
                # Añadimos un error general al formulario para mostrarlo en la plantilla.
                form.add_error(None, 'Error: Ya existe un asistente con este nombre para este evento.')
    else: # GET
        form = AsistenteForm()
    # Renderizamos la plantilla con el formulario (ya sea nuevo o con el error).
    return render(request, 'crear_asistente.html', {"form": form})

def signout(request):
    logout(request)
    return redirect('home')


def signin(request):
    if request.method == 'GET':
        form = AuthenticationForm()
        return render(request, 'signin.html', {"form": form})
    else: # POST
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'signin.html', {"form": form})

# -------------- aqui en adelante es es la parte de nuestro ejercicio del profesor ---------------- 

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User

def user_profile_view(request, user_id: int):
    """
    Vista que muestra el perfil de un usuario específico.
    """
    # Esta línea intenta obtener el usuario por su ID.
    # Si no lo encuentra, la ejecución se detiene y Django devuelve una página 404.
    # No necesitas un bloque try/except.
    usuario = get_object_or_404(User, id=user_id)
    
    # Si el código llega hasta aquí, significa que el usuario fue encontrado.
    # Ahora puedes pasar el objeto 'usuario' a tu plantilla HTML.
    context = {
        'user_profile': usuario
    }
    
    return render(request, 'profiles/user_profile.html', context)

# --- Nueva vista para el detalle del evento ---
