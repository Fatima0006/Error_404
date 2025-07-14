from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError

# Create your views here.


def home(request):
    return render(request, 'home.html')


def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {"form": UserCreationForm})
    else:

        if request.POST["password1"] == request.POST["password2"]:
            try:
                user = User.objects.create_user(
                    request.POST["username"], password=request.POST["password1"])
                user.save()
                login(request, user)
                return redirect('tasks')
            except IntegrityError:
                return render(request, 'signup.html', {"form": UserCreationForm, "error": "Username already exists."})
        return render(request, 'signup.html', {"form": UserCreationForm, "error": "Passwords did not match."})


def check_in(request):
    return render(request, 'check_in.html')


def tasks(request):
    return render(request, 'tasks.html')  # a


def signout(request):
    logout(request)
    return render(request, 'home.html', {"error": "You are not logged in."})


def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {"form": AuthenticationForm})
    else:
        user = authenticate(
            request, username=request.POST["username"], password=request.POST["password"])
        if user is None:
            return render(request, 'signin.html', {"form": AuthenticationForm, "error": "Username or password is incorrect."})
        else:
            login(request, user)
            return redirect('tasks')#

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
    usuario = get_object_or_404(User, id=1)
    
    # Si el código llega hasta aquí, significa que el usuario fue encontrado.
    # Ahora puedes pasar el objeto 'usuario' a tu plantilla HTML.
    context = {
        'user_profile': usuario
    }
    
    return render(request, 'profiles/user_profile.html', context)