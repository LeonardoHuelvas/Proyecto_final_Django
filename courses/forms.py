from django import forms
from .models import Course, Material, Exam, Question, Answer, Enrollment, Grade, Forum, Post, User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm

class SignupForm(UserCreationForm):
    """
    Formulario para el registro de nuevos usuarios.
    """
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control form-control-user', 'placeholder': 'Nombre de usuario'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control form-control-user', 'placeholder': 'Contraseña'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control form-control-user', 'placeholder': 'Confirmar contraseña'}),
        }

class LoginForm(forms.Form):
    """
    Formulario para el inicio de sesión de usuarios.
    """
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control form-control-user', 'placeholder': 'Usuario'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control form-control-user', 'placeholder': 'Contraseña'}))

class UserUpdateForm(forms.ModelForm):
    """
    Formulario para actualizar la información del usuario.
    """
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control form-control-user', 'placeholder': 'Nombre de usuario'}),
            'email': forms.EmailInput(attrs={'class': 'form-control form-control-user', 'placeholder': 'Correo electrónico'}),
        }

class CourseForm(forms.ModelForm):
    """
    Formulario para la creación y edición de cursos.
    """
    class Meta:
        model = Course
        fields = ['title', 'description', 'start_date', 'end_date', 'instructor', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'instructor': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

    def clean_end_date(self):
        """
        Validación para asegurarse de que la fecha de finalización no sea anterior a la fecha de inicio.
        """
        start_date = self.cleaned_data.get('start_date')
        end_date = self.cleaned_data.get('end_date')
        if end_date < start_date:
            raise forms.ValidationError("La fecha de finalización no puede ser anterior a la fecha de inicio.")
        return end_date

class MaterialForm(forms.ModelForm):
    """
    Formulario para la creación y edición de materiales del curso.
    """
    class Meta:
        model = Material
        fields = ['title', 'course', 'file_type', 'file', 'video_url']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'file_type': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'video_url': forms.URLInput(attrs={'class': 'form-control'}),
        }

class InstructorForm(forms.ModelForm):
    """
    Formulario para la creación y edición de instructores.
    """
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'role']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        }

    def __init__(self, *args, **kwargs):
        """
        Inicializa el formulario, estableciendo el rol predeterminado como 'instructor' y haciéndolo de solo lectura.
        """
        super(InstructorForm, self).__init__(*args, **kwargs)
        self.fields['role'].initial = 'instructor'
        self.fields['role'].widget.attrs['readonly'] = True

    def save(self, commit=True):
        """
        Sobrescribe el método save para asegurarse de que la contraseña esté configurada correctamente.
        """
        user = super(InstructorForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user        

class CustomAuthenticationForm(AuthenticationForm):
    """
    Formulario personalizado para la autenticación de usuarios.
    """
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control form-control-user', 'placeholder': 'Usuario...'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control form-control-user', 'placeholder': 'Contraseña'}))

class EnrollmentForm(forms.ModelForm):
    """
    Formulario para la inscripción de estudiantes en los cursos.
    """
    class Meta:
        model = Enrollment
        fields = ['course']
        widgets = {
            'course': forms.HiddenInput()
        }

class ExamForm(forms.ModelForm):
    """
    Formulario para la creación y edición de exámenes.
    """
    class Meta:
        model = Exam
        fields = ['title', 'total_marks']



class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'question_type']

class AnswerForm(forms.Form):
    answer = forms.ChoiceField(widget=forms.RadioSelect)

    def __init__(self, *args, **kwargs):
        question = kwargs.pop('question')
        super().__init__(*args, **kwargs)
        self.fields['answer'].choices = [(answer.id, answer.text) for answer in question.answers.all()]
        
        
class ForumForm(forms.ModelForm):
    class Meta:
        model = Forum
        fields = ['title']

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content']
        
        
class UserProfileForm(UserChangeForm):
    password = None  # Excluir el campo de contraseña

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'profile_picture')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }