from django.db import models # Este recuerda dejarlo asi
from django.contrib.auth.models import User # Importa el modelo de usuario de Django
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.utils import timezone

# Create your models here.
class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    datecompleted =models.DateTimeField(null=True, blank=True)
    important = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')

    def __str__(self):
        return self.title + ' - by ' + self.user.username  
    



#    Sepáracion de modelos ------------------------------------------------------------------------------------------------------



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
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='eventos', null=True, blank=True
    )

    def __str__(self):
        # Esta representación amigable se usará en el panel de administración de Django.
        return f"{self.nombre} ({self.fecha})"

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
        help_text="Nombre completo del asistente"
    )
    #NUEVO: Enlace directo al evento al que pertenece el asistente.
    # Esto establece la relación "un asistente pertenece a un solo evento".
    evento = models.ForeignKey(
            Evento,
            on_delete=models.CASCADE,
            related_name='asistentes'
         )

    def __str__(self):
        # Hacemos más clara la representación, mostrando el evento.
        return f"{self.nombre} ({self.evento.nombre})"

    class Meta:
        ordering = ['nombre'] # Ordena los asistentes alfabéticamente.
        # NUEVO: Asegura que no haya dos asistentes con el mismo nombre en el MISMO evento.
        unique_together = ('evento', 'nombre')


# --- Modelo de Registros ---
# Es el corazón del sistema, conecta Eventos y Asistentes y controla los tiempos.
class Registro(models.Model):
    """
    Registra la asistencia de un Asistente a un Evento,
    incluyendo horas de entrada (check-in) y salida (check-out).
    """
    asistente = models.ForeignKey(
        Asistente, on_delete=models.CASCADE,
        help_text="Asistente que realiza el check-in/out"
    )
    check_in = models.DateTimeField(
        null=True, blank=True,
        help_text="Fecha y hora exactas de entrada al evento"
    )
    check_out = models.DateTimeField(
        null=True, blank=True,
        help_text="Fecha y hora exactas de salida del evento (vacío si sigue dentro)"
    )

    # --- Propiedades y validaciones ---
    @property
    def evento(self):
        """
        Propiedad para acceder fácilmente al evento del asistente.
        Permite que el resto del código siga usando `registro.evento`.
        """
        return self.asistente.evento

    @property
    def duracion(self):
        """
        Calcula la duración de la estancia del asistente en minutos.
        Devuelve None si no hay check_out.
        """
        if self.check_in and self.check_out:
            return (self.check_out - self.check_in).total_seconds() / 60
        return None

    def clean(self):
        """
        Validaciones personalizadas que se ejecutan antes de guardar.
        """
        if self.check_in and self.check_out and self.check_out < self.check_in:
            raise ValidationError("La salida no puede ser antes de la entrada.")

    def save(self, *args, **kwargs):
        """
        Sobrescribimos save para asegurarnos de que clean() se ejecute siempre.
        """
        self.full_clean()  # Ejecuta validaciones
        super().save(*args, **kwargs)

    def __str__(self):
        estado = "Dentro" if self.check_out is None else "Salió"
        # Accedemos al evento a través de la nueva propiedad
        return f"{self.asistente.nombre} en '{self.evento.nombre}' ({estado})"

    class Meta:
        ordering = ['-check_in']
        # Evitar múltiples check-ins activos por asistente
        constraints = [
            models.UniqueConstraint(
                # MODIFICADO: La unicidad ahora es solo por asistente.
                fields=['asistente'],
                condition=Q(check_out__isnull=True),
                name='unique_active_checkin_per_assistant'
            )
        ]

    