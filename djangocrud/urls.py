"""
URL configuration for djangocrud project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from tasks import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path ('',views.home, name='home'),
    path ('signup/', views.signup, name='signup'),
    path('eventos/',views.eventos,name='eventos'),
    path('eventos/<int:evento_id>/', views.evento_detail, name='evento_detail'),
    path('tasks/',views.tasks,name='tasks'),
    path('tasks/create/',views.create_task,name= 'create_task'),
    path('tasks/<int:task_id>/',views.task_detail,name= 'task_detail'),
    # URL para el nuevo formulario de registro de asistencia
    path('evento/<int:evento_id>/asistencia/', views.kiosco_asistencia, name='kiosco_asistencia'),
    path('asistencia/crear/',views.crear_asistente,name= 'crear_asistente'),
    path('event/create/',views.create_event,name='create_event'),
    path('logout/',views.signout,name='logout'),
    path('signin/',views.signin,name='signin'),
    path('eventos/<int:evento_id>/delete/', views.delete_event, name='delete_event'),
]
