# Plataforma de Cursos en Línea

## Descripción

Este proyecto es una plataforma de cursos en línea que permite a los usuarios inscribirse en cursos, ver material educativo y realizar exámenes. Los instructores pueden crear, editar y eliminar cursos, así como subir material y diseñar exámenes. Está construido utilizando Django y Django Rest Framework.

## Características

### Usuarios

- Registro e inicio de sesión.
- Inscripción en cursos.
- Visualización de material educativo.
- Realización de exámenes.

### Instructores

- Creación, edición y eliminación de cursos.
- Subida de material educativo.
- Diseño de exámenes con preguntas de tipo texto y selección múltiple.

### Administradores

- Gestión de usuarios.
- Gestión de cursos y material educativo.
- Gestión de exámenes y preguntas.

## Instalación

### Prerrequisitos

- Python 3.8 o superior
- Git

### Pasos

1. **Clona el repositorio**:

    ```bash
    git clone https://github.com/tu_usuario/tu_repositorio.git
    cd tu_repositorio
    ```

2. **Crea un entorno virtual y actívalo**:

    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ```

3. **Instala las dependencias**:

    ```bash
    pip install -r requirements.txt
    ```

4. **Realiza las migraciones de la base de datos**:

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

5. **Crea un superusuario para acceder al panel de administración**:

    ```bash
    python manage.py createsuperuser
    ```

6. **Ejecuta el servidor de desarrollo**:

    ```bash
    python manage.py runserver
    ```

7. **Accede a la aplicación en tu navegador**:

    ```
    http://127.0.0.1:8000/
    ```

## Uso

### Usuarios

1. Regístrate e inicia sesión.
2. Inscríbete en cursos disponibles.
3. Visualiza el material educativo del curso en el que estás inscrito.
4. Realiza exámenes y consulta tus resultados.


### Instructores

1. Inicia sesión como instructor.
2. Crea, edita y elimina cursos.
3. Sube material educativo para tus cursos.
4. Diseña exámenes y agrega preguntas.

### Administradores

1. Inicia sesión como administrador.
2. Gestiona usuarios, cursos, materiales y exámenes desde el panel de administración.

## Estructura del Proyecto

.
├── courses/
│ ├── migrations/
│ ├── static/
│ ├── templates/
│ ├── init.py
│ ├── admin.py
│ ├── apps.py
│ ├── forms.py
│ ├── models.py
│ ├── tests.py
│ ├── urls.py
│ └── views.py
├── online_courses/
│ ├── init.py
│ ├── asgi.py
│ ├── settings.py
│ ├── urls.py
│ └── wsgi.py
├── manage.py
├── requirements.txt
└── README.md



- `courses/`: Aplicación principal que contiene los modelos, vistas, formularios y plantillas.
- `online_courses/`: Configuración principal del proyecto.
- `static/`: Archivos estáticos como CSS, JS e imágenes.
- `templates/`: Plantillas HTML para la aplicación.
- `manage.py`: Script para la gestión del proyecto.
- `requirements.txt`: Archivo con las dependencias del proyecto.

## Modelos Principales

- **Course**: Modelo para los cursos.
- **Material**: Modelo para el material educativo de los cursos.
- **Exam**: Modelo para los exámenes de los cursos.
- **Question**: Modelo para las preguntas de los exámenes.
- **Answer**: Modelo para las respuestas de las preguntas.
- **Grade**: Modelo para almacenar las calificaciones de los estudiantes.

## Contribuciones

Las contribuciones son bienvenidas. Si deseas contribuir, por favor abre un issue o envía un pull request.

## Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo `LICENSE` para más detalles.

## Contacto

Para cualquier consulta o soporte, por favor contacta a [lejhubo01@hotmail.com](mailto:lejhubo01@hotmail.com).
