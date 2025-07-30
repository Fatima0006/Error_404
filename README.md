# Error_404
--------------------
Gogo estuvo aqui.

## Requisitos del proyecto 

8. Gestor de Asistencia con Check-in y Reportes
Descripción:
App para gestionar entradas/salidas de asistentes a eventos.
Requerimientos funcionales:
CRUD de eventos y asistentes.
Registro de entrada/salida (check-in/check-out).
Reporte de duración por evento y asistente.
Base de datos sugerida:
Eventos(id, nombre, fecha)
Asistentes(id, nombre)
Registros(id, evento_id, asistente_id, check_in, check_out)
Reglas de negocio:
Evitar múltiples check-ins por evento.
Calcular duración entre entrada y salida.
Objetivo técnico:
Evaluar control de tiempos, cálculo de duración y prevención de duplicados.


- Python 3.12 (o la versión que uses)
- pip
-django 5.2.3

-- Definir una funcion para traer elementos por ID

Anotaciones de SEM 

Necesito hacer la relaciones entre eventro y asistentes 


## Cómo correr este proyecto

```bash
# Clona el repo
git clone https://github.com/Fatima0006/Error_404.git
cd Error 404

borra el entorno virtual de la carpeta de error404 y luego inicia el siguente paso 

# Crea entorno virtual
python -m venv venv
source venv/bin/activate   # En Windows: venv\Scripts\activate

# Instala dependencias
pip install -r requirements.txt -- paso pendiente ( pasa al siguente)
pip install django

# Corre el programa
python manage.py runserver
python manage.py migrate  # solamente una vez para correr la DB

Esto es un pre-view 

para apagar venv

