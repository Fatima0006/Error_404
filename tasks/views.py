from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm

# Create your views here.

def  home (request):
    return render(request, 'home.html',{
        
})

def  signup (request):

    if request.method == 'GET': 
        print('enviando Formulario')
    else:
        print ('obteniendo datos') 
        print(request.POST)

    return render(request, 'signup.html',{
        'from': UserCreationForm
})