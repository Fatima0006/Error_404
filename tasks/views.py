from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import taskForm, EventForm, AsistenteForm, KioscoAsistenciaForm, Asistente
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
            return redirect('eventos')
        else:
            # El formulario ya contiene los errores, solo hay que volver a mostrarlo
            return render(request, 'signup.html', {"form": form})

@login_required
def eventos(request):
    eventos_list = Evento.objects.filter(user=request.user)
    return render(request, 'eventos.html', {"eventos": eventos_list})


@login_required
def tasks(request):
    tasks = Task.objects.filter(user=request.user)
    return render(request, 'tasks.html', {"tasks": tasks})

@login_required
def create_task(request):
    if request.method == 'POST':
        form = taskForm(request.POST)
        if form.is_valid():
            new_task = form.save(commit=False)
            new_task.user = request.user # Se asocia la tarea al usuario logueado
            new_task.save()
            return redirect('tasks')
    else: # GET
        form = taskForm()
    return render(request, 'create_task.html', {"form": form})

@login_required
def task_detail(request, task_id):
    # Se añade 'user=request.user' para asegurar que el usuario solo puede ver sus propias tareas.
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'GET':
        form = taskForm(instance=task)
        return render(request, 'task_detail.html', {"tasks": task, "form": form})
    else : 
        form = taskForm(request.POST, instance=task)
        form.save()
        return redirect('tasks')

@login_required
def complete_task(request, task_id):
    # Se añade 'user=request.user' para asegurar que el usuario solo puede completar sus propias tareas.
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    task.datecompleted = timezone.now()
    task.save()
    return redirect('tasks')
 # -------------Checar esta parte para ver como es que funcionaria BD


from django.forms import modelformset_factory

@login_required
def evento_detail(request, evento_id):
    # Se añade 'user=request.user' para asegurar que el usuario solo puede ver sus propios eventos.
    evento = get_object_or_404(Evento, pk=evento_id, user=request.user)
    
    # 1. Crear el Formset para los Asistentes, ahora con un campo extra para añadir.
    AsistenteFormSet = modelformset_factory(Asistente, form=AsistenteForm, extra=1, can_delete=True)

    if request.method == 'POST':
        form = EventForm(request.POST, instance=evento, prefix='evento')
        formset = AsistenteFormSet(request.POST, queryset=evento.asistentes.all(), prefix='asistentes')
        
        if form.is_valid() and formset.is_valid():
            form.save()
            
            # Procesar el formset para asociar nuevos asistentes con el evento
            try:
                instances = formset.save(commit=False)
                for instance in instances:
                    instance.evento = evento  # Asignar el evento actual
                    instance.save()
                
                # Manejar la eliminación
                for obj in formset.deleted_objects:
                    obj.delete()

                messages.success(request, "¡Cambios guardados exitosamente!")
                return redirect('evento_detail', evento_id=evento.id)

            except IntegrityError:
                messages.error(request, "Error: Ya existe un asistente con este nombre para este evento." \
                " Registra otra persona")

    else: # GET
        form = EventForm(instance=evento, prefix='evento')
        formset = AsistenteFormSet(queryset=evento.asistentes.all(), prefix='asistentes')

    context = {
        'evento': evento,
        'form': form,
        'formset': formset,
    }
    return render(request, 'evento_detail.html', context)

@login_required
def kiosco_asistencia(request, evento_id):
    # Se añade 'user=request.user' para asegurar que el usuario solo puede gestionar sus propios eventos.
    evento = get_object_or_404(Evento, pk=evento_id, user=request.user)
    
    if request.method == 'POST':
        form = KioscoAsistenciaForm(request.POST, evento=evento)
        if form.is_valid():
            asistente_seleccionado = form.cleaned_data['asistente']
            
            # Lógica mejorada: Buscar un registro ACTIVO (sin check-out) para este asistente.
            # Esto permite que un asistente pueda salir y volver a entrar.
            registro_activo = Registro.objects.filter(
                asistente=asistente_seleccionado,
                check_out__isnull=True
            ).first()


            if registro_activo:
                # Si está dentro, hacemos check-out.
                registro_activo.check_out = timezone.now()
                registro_activo.save()
                messages.success(request, f"Se registró la SALIDA de {asistente_seleccionado.nombre}.")
            else:
                # Buscar si ya existe algún registro anterior (ya hizo check-out)
                registro_anterior = Registro.objects.filter(
                    asistente=asistente_seleccionado
                ).exclude(check_out__isnull=True).exists()
                if registro_anterior:
                    # Si ya hizo check-out antes, NO permitir re-entrada
                    messages.error(request, f"{asistente_seleccionado.nombre} ya registró su salida y no puede volver a entrar a este evento.")
                else:
                    # Si es su primera vez, hacemos un nuevo check-in.
                    Registro.objects.create(
                        asistente=asistente_seleccionado,
                        check_in=timezone.now()
                    )
                    messages.success(request, f"Se registró la ENTRADA de {asistente_seleccionado.nombre}.")

            # Redirigimos a la misma página para ver el resultado
            return redirect('kiosco_asistencia', evento_id=evento.id)
    else: # GET
        form = KioscoAsistenciaForm(evento=evento)

    # 4. Preparamos la información para la tabla de estado (forma optimizada para evitar N+1 queries)
    asistentes_del_evento = evento.asistentes.all()
    # Obtenemos todos los registros de los asistentes de este evento en una sola consulta
    todos_los_registros = Registro.objects.filter(
        asistente__in=asistentes_del_evento
    ).order_by('asistente_id', '-check_in')

    # Creamos un diccionario para guardar solo el último registro de cada asistente
    ultimo_registro_por_asistente = {}
    for registro in todos_los_registros:
        if registro.asistente_id not in ultimo_registro_por_asistente:
            ultimo_registro_por_asistente[registro.asistente_id] = registro

    # Construimos la lista final para la plantilla
    asistentes_con_estado = []
    for asistente in asistentes_del_evento:
        asistentes_con_estado.append({
            'asistente': asistente,
            'registro': ultimo_registro_por_asistente.get(asistente.id)
        })

    context = {
        'evento': evento,
        'form': form,
        'asistentes_con_estado': asistentes_con_estado,
    }
    return render(request, 'registrar_asistente.html', context)
        
@login_required
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
            # Redirigimos a la lista de eventos para una mejor experiencia de usuario.
            return redirect('eventos')
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

@login_required
def delete_event(request, evento_id):
    if request.method == 'POST':
        # Busca el evento asegurándose de que le pertenece al usuario logueado
        evento = get_object_or_404(Evento, pk=evento_id, user=request.user)
        # Elimina el evento de la base de datos
        evento.delete()
        messages.success(request, f"El evento '{evento.nombre}' ha sido eliminado.")
    # Redirige a la lista de eventos
    return redirect('eventos')
# --- Nueva vista para el detalle del evento ---
