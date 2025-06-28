from django.db import models # Este recuerda dejarlo asi
from django.contrib.auth.models import User # Importa el modelo de usuario de Django
# Create your models here.
class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    datecompleted = models.BooleanField(default=False)
    important = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    
#    Sepáracion de modelos ------------------------------------------------------------------------------------------------------


from django.db.models import Q
from django.core.exceptions import ValidationError
from django.utils import timezone

# --- Modelo de Eventos ---
# Almacena la información de cada evento.
class Evento(models.Model):
    """
    Representa un evento con un nombre y una fecha específica.
    """
    nombre = models.CharField(
        max_length=200, 
        help_text="Nombre del evento (ej: Conferencia Anual 2025)"
    )
    fecha = models.DateField(
        help_text="Fecha en que se realiza el evento"
    )

    def __str__(self):
        # Esta representación amigable se usará en el panel de administración de Django.
        return f"{self.nombre} ({self.fecha.strftime('%d-%m-%Y')})"

    class Meta:
        ordering = ['-fecha'] # Ordena los eventos por fecha, del más reciente al más antiguo.


# --- Modelo de Asistentes ---
# Almacena la lista maestra de todas las personas que pueden asistir a los eventos.
class Asistente(models.Model):
    """
    Representa a una persona que puede asistir a un evento.
    """
    nombre = models.CharField(
        max_length=200, 
        unique=True, # Evita tener dos asistentes con el mismo nombre.
        help_text="Nombre completo del asistente"
    )

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ['nombre'] # Ordena los asistentes alfabéticamente.


# --- Modelo de Registros ---
# Es el corazón del sistema, conecta Eventos y Asistentes y controla los tiempos.
class Registro(models.Model):
    """
    Registra la asistencia de un Asistente a un Evento, incluyendo
    las horas de entrada (check-in) y salida (check-out).
    """
    evento = models.ForeignKey(
        Evento, 
        on_delete=models.CASCADE, 
        help_text="Evento al que se registra la asistencia"
    )
    asistente = models.ForeignKey(
        Asistente, 
        on_delete=models.CASCADE, 
        help_text="Asistente que realiza el check-in/out"
    )
    check_in = models.DateTimeField(
        help_text="Fecha y hora exactas en que el asistente entra al evento"
    )
    check_out = models.DateTimeField(
        null=True,      # Permite que este campo esté vacío (cuando alguien ha hecho check-in pero no check-out).
        blank=True,     # Permite que el campo no sea requerido en formularios (como el admin de Django).
        help_text="Fecha y hora exactas en que el asistente sale del evento. Vacío si aún está dentro."
    )

    @property
    def duracion(self):
        """
        Calcula la duración de la estancia del asistente en el evento.
        Este es un método @property, por lo que puedes llamarlo como un atributo: registro.duracion
        """
        if self.check_in and self.check_out:
            # Devuelve un objeto `timedelta` que representa la diferencia.
            return self.check_out - self.check_in
        return None # Devuelve None si la persona no ha hecho check-out aún.

    def clean(self):
        """
        Añade validaciones personalizadas que se ejecutan antes de guardar.
        """
        # Valida que la hora de salida no sea anterior a la de entrada.
        if self.check_in and self.check_out and self.check_out < self.check_in:
            raise ValidationError("La hora de check-out no puede ser anterior a la hora de check-in.")

    def __str__(self):
        estado = "Dentro" if self.check_out is None else "Salió"
        return f"{self.asistente.nombre} en '{self.evento.nombre}' ({estado})"

    class Meta:
        # Ordena los registros por la hora de entrada.
        ordering = ['-check_in']
        
        # REGLA DE NEGOCIO: Evitar múltiples check-ins por evento.
        # Esta restricción a nivel de base de datos asegura que la combinación de
        # 'evento' y 'asistente' sea única para todos los registros
        # que AÚN NO tienen un 'check_out'.
        constraints = [
            models.UniqueConstraint(
                fields=['evento', 'asistente'], 
                condition=Q(check_out__isnull=True),
                name='unique_active_checkin_per_event'
            )
        ]