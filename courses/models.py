from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.db import models

class UserManager(BaseUserManager):
    """
    Manager personalizado para el modelo User con métodos para crear usuarios y superusuarios.
    """
    def create_user(self, username, email, password=None, **extra_fields):
        """
        Crea y guarda un usuario con el nombre de usuario, correo electrónico y contraseña proporcionados.
        """
        if not email:
            raise ValueError('El campo de correo electrónico debe estar configurado.')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        """
        Crea y guarda un superusuario con el nombre de usuario, correo electrónico y contraseña proporcionados.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True.')
        if extra_fields.get('role') != 'admin':
            raise ValueError('Superuser debe tener role="admin".')

        return self.create_user(username, email, password, **extra_fields)

class User(AbstractUser):
    """
    Modelo personalizado de usuario que incluye roles adicionales y campos relacionados.
    """
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('instructor', 'Instructor'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    groups = models.ManyToManyField(Group, related_name='custom_user_set')
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_set')
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

    objects = UserManager()

    def save(self, *args, **kwargs):
        """
        Sobrescribe el método save para asegurarse de que los superusuarios tengan el rol de administrador.
        """
        if self.is_superuser:
            self.role = 'admin'
        super().save(*args, **kwargs)

class Course(models.Model):
    """
    Modelo para los cursos.
    """
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'instructor'})
    image = models.ImageField(upload_to='course_images/', null=True, blank=True)
    video_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title

    def get_youtube_id(self):
        """
        Obtiene el ID de YouTube del video del curso.
        """
        if self.video_url and "youtube.com" in self.video_url:
            return self.video_url.split("v=")[1].split("&")[0]
        elif self.video_url and "youtu.be" in self.video_url:
            return self.video_url.split("/")[-1]
        return None

    def get_youtube_thumbnail(self):
        """
        Obtiene la miniatura del video de YouTube del curso.
        """
        youtube_id = self.get_youtube_id()
        if (youtube_id):
            return f"https://img.youtube.com/vi/{youtube_id}/0.jpg"
        return None

class Enrollment(models.Model):
    """
    Modelo para las inscripciones de los estudiantes en los cursos.
    """
    STATUS_CHOICES = (
        ('inscrito', 'Inscrito'),
        ('en_espera', 'En Espera'),
        ('cancelado', 'Cancelado'),
    )

    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrollment_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='en_espera')

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.username} en {self.course.title}"

    def enroll(self):
        """
        Cambia el estado de la inscripción a 'inscrito'.
        """
        if self.status != 'inscrito':
            self.status = 'inscrito'
            self.save()

    def cancel_enrollment(self):
        """
        Cancela la inscripción cambiando el estado a 'cancelado'.
        """
        if self.status == 'inscrito':
            self.status = 'cancelado'
            self.save()

    def is_enrolled(self):
        """
        Verifica si el estudiante está inscrito en el curso.
        """
        return self.status == 'inscrito'

class Material(models.Model):
    """
    Modelo para los materiales del curso.
    """
    title = models.CharField(max_length=200)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='materials')
    file_type = models.CharField(max_length=50)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='materials/', blank=True, null=True)
    video_url = models.URLField(max_length=200, blank=True, null=True)

    @staticmethod
    def extract_youtube_id(url):
        """
        Extrae el ID de YouTube de una URL.
        """
        if "youtube.com" in url:
            return url.split("v=")[1].split("&")[0]
        elif "youtu.be" in url:
            return url.split("/")[-1]
        return None

    @property
    def get_youtube_id(self):
        """
        Obtiene el ID de YouTube del video del material.
        """
        return self.extract_youtube_id(self.video_url)

class Exam(models.Model):
    """
    Modelo para los exámenes.
    """
    title = models.CharField(max_length=200)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='exams')
    total_marks = models.IntegerField()

    def __str__(self):
        return self.title

class Question(models.Model):
    """
    Modelo para las preguntas del examen.
    """
    QUESTION_TYPES = (
        ('text', 'Text'),
        ('multiple_choice', 'Multiple Choice'),
    )
    text = models.TextField()
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')
    question_type = models.CharField(max_length=50, choices=QUESTION_TYPES)

    def __str__(self):
        return self.text

class Answer(models.Model):
    """
    Modelo para las respuestas a las preguntas del examen.
    """
    text = models.TextField()
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class Grade(models.Model):
    """
    Modelo para almacenar las calificaciones de los estudiantes.
    """
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    marks_obtained = models.IntegerField()

    def __str__(self):
        return f"{self.student.username}: {self.marks_obtained} en {self.exam.title}"

class Forum(models.Model):
    """
    Modelo para los foros de discusión de los cursos.
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='forums')
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Post(models.Model):
    """
    Modelo para las publicaciones en los foros.
    """
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Post by {self.created_by.username} in {self.forum.title}"

class Profile(models.Model):
    """
    Modelo para el perfil de usuario.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'
