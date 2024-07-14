"""
views.py

Este archivo contiene las vistas para la aplicación de cursos en línea. Incluye vistas para gestionar cursos, materiales, instructores, exámenes y foros, así como las vistas de autenticación y los mixins necesarios para la autorización.
"""

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from rest_framework import viewsets
from django.contrib.auth.decorators import login_required, user_passes_test
from rest_framework.permissions import IsAuthenticated
from django.urls import reverse_lazy, reverse
from django.contrib.auth.views import LoginView 
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from .forms import (
    ExamForm, ForumForm, PostForm, UserProfileForm, CourseForm, InstructorForm, CustomAuthenticationForm, 
    MaterialForm, SignupForm, LoginForm, AnswerForm
)
from .models import (
    Course, Enrollment, Forum, Material, Exam, Post, Question, Answer, Grade, User
)
from .serializers import CourseSerializer, MaterialSerializer, ExamSerializer, QuestionSerializer, AnswerSerializer
from django.contrib.auth.models import Group, Permission
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator
from django.utils import timezone
from datetime import timedelta


class StudentAccessMixin(UserPassesTestMixin):
    """
    Mixin para restringir el acceso de los estudiantes.
    """
    def test_func(self):
        return self.request.user.role != 'student'

    def handle_no_permission(self):
        return render(self.request, '404.html')


class StudentCheckMixin:
    """
    Mixin para verificar si el usuario es un estudiante.
    """
    def get_user_courses(self):
        user = self.request.user
        if user.is_authenticated and user.role == 'student':
            return Enrollment.objects.filter(student=user).values_list('course_id', flat=True)
        return []


class RoleRequiredMixin(UserPassesTestMixin):
    """
    Mixin para verificar el rol del usuario.
    """
    required_role = None

    def test_func(self):
        return self.request.user.role == self.required_role

    def handle_no_permission(self):
        return render(self.request, '404.html')


class IndexView(LoginRequiredMixin, TemplateView, StudentCheckMixin):
    """
    Vista para la página principal.
    """
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        """
        Agrega los cursos y exámenes al contexto.
        """
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['courses'] = Course.objects.all()
        context['exams'] = Exam.objects.all()
        context['enrolled_courses'] = self.get_user_courses()
        return context


class CourseListView(LoginRequiredMixin, StudentAccessMixin, ListView, StudentCheckMixin):
    """
    Vista para listar los cursos.
    """
    model = Course
    template_name = 'course/course_list.html'
    context_object_name = 'courses'

    def get_queryset(self):
        """
        Devuelve los cursos en los que el estudiante está inscrito o todos los cursos para otros usuarios.
        """
        user = self.request.user
        if user.role == 'student':
            return Course.objects.filter(enrollment__student=user)
        return Course.objects.all()


class CourseDetailView(LoginRequiredMixin, DetailView):
    """
    Vista para los detalles de un curso.
    """
    model = Course
    template_name = 'course/course_detail.html'
    context_object_name = 'course'

    def get(self, request, *args, **kwargs):
        """
        Verifica la inscripción del estudiante antes de mostrar el curso.
        """
        self.object = self.get_object()
        user = request.user
        if user.role == 'student' and not Enrollment.objects.filter(student=user, course=self.object).exists():
            messages.error(request, 'Debes inscribirte en el curso para verlo.')
            return redirect('enroll_course', pk=self.object.pk)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Agrega los exámenes del curso al contexto.
        """
        context = super().get_context_data(**kwargs)
        context['exams'] = self.object.exams.all()
        context['back_url'] = reverse('student_dashboard') if self.request.user.role == 'student' else reverse('course_list')
        return context


class CourseCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Vista para crear un curso.
    """
    model = Course
    form_class = CourseForm
    template_name = 'course/course_form.html'
    success_url = reverse_lazy('course_list')

    def test_func(self):
        """
        Verifica si el usuario es un superusuario o un instructor.
        """
        return self.request.user.is_superuser or self.request.user.role == 'instructor'

    def handle_no_permission(self):
        """
        Maneja el caso en el que el usuario no tiene permisos para crear un curso.
        """
        return render(self.request, '404.html')


class CourseUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Vista para actualizar un curso.
    """
    model = Course
    form_class = CourseForm
    template_name = 'course/course_form.html'
    success_url = reverse_lazy('course_list')

    def test_func(self):
        """
        Verifica si el usuario es el instructor del curso o un superusuario.
        """
        course = self.get_object()
        return self.request.user.is_superuser or (self.request.user.role == 'instructor' and course.instructor == self.request.user)

    def handle_no_permission(self):
        """
        Maneja el caso en el que el usuario no tiene permisos para actualizar el curso.
        """
        return render(self.request, '404.html')


class CourseDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Vista para eliminar un curso.
    """
    model = Course
    template_name = 'course/course_confirm_delete.html'
    success_url = reverse_lazy('course_list')

    def test_func(self):
        """
        Verifica si el usuario es un superusuario o un instructor.
        """
        return self.request.user.is_superuser or self.request.user.role == 'instructor'

    def handle_no_permission(self):
        """
        Maneja el caso en el que el usuario no tiene permisos para eliminar el curso.
        """
        return render(self.request, '404.html')


class MaterialListView(LoginRequiredMixin, StudentAccessMixin, ListView):
    """
    Vista para listar los materiales de los cursos.
    """
    model = Material
    template_name = 'material/material_list.html'
    context_object_name = 'materials'

    def get_queryset(self):
        """
        Devuelve los materiales del instructor o ningún material para otros usuarios.
        """
        user = self.request.user
        if user.role == 'instructor':
            return Material.objects.filter(course__instructor=user)
        return Material.objects.none()


class MaterialDetailView(LoginRequiredMixin, StudentAccessMixin, UserPassesTestMixin, DetailView):
    """
    Vista para los detalles de un material del curso.
    """
    model = Material
    template_name = 'material/material_detail.html'
    context_object_name = 'material'

    def test_func(self):
        """
        Verifica si el usuario es el instructor del material o un superusuario.
        """
        material = self.get_object()
        return self.request.user == material.course.instructor or self.request.user.is_superuser

    def handle_no_permission(self):
        """
        Maneja el caso en el que el usuario no tiene permisos para ver el material.
        """
        return render(self.request, '404.html')


class MaterialCreateView(LoginRequiredMixin, StudentAccessMixin, UserPassesTestMixin, CreateView):
    """
    Vista para crear un material del curso.
    """
    model = Material
    form_class = MaterialForm
    template_name = 'material/material_form.html'
    success_url = reverse_lazy('material_list')

    def test_func(self):
        """
        Verifica si el usuario es un superusuario o un instructor.
        """
        return self.request.user.is_superuser or self.request.user.role == 'instructor'

    def handle_no_permission(self):
        """
        Maneja el caso en el que el usuario no tiene permisos para crear el material.
        """
        return render(self.request, '404.html')


class MaterialUpdateView(LoginRequiredMixin, StudentAccessMixin, UserPassesTestMixin, UpdateView):
    """
    Vista para actualizar un material del curso.
    """
    model = Material
    form_class = MaterialForm
    template_name = 'material/material_form.html'
    success_url = reverse_lazy('material_list')

    def test_func(self):
        """
        Verifica si el usuario es el instructor del material o un superusuario.
        """
        material = self.get_object()
        return self.request.user.is_superuser or (self.request.user.role == 'instructor' and material.course.instructor == self.request.user)

    def handle_no_permission(self):
        """
        Maneja el caso en el que el usuario no tiene permisos para actualizar el material.
        """
        return render(self.request, '404.html')


class MaterialDeleteView(LoginRequiredMixin, StudentAccessMixin, UserPassesTestMixin, DeleteView):
    """
    Vista para eliminar un material del curso.
    """
    model = Material
    template_name = 'material/material_confirm_delete.html'
    success_url = reverse_lazy('material_list')

    def test_func(self):
        """
        Verifica si el usuario es un superusuario o un instructor.
        """
        return self.request.user.is_superuser or self.request.user.role == 'instructor'

    def handle_no_permission(self):
        """
        Maneja el caso en el que el usuario no tiene permisos para eliminar el material.
        """
        return render(self.request, '404.html')


class CourseViewSet(viewsets.ModelViewSet):
    """
    API ViewSet para los cursos.
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]


class MaterialViewSet(viewsets.ModelViewSet):
    """
    API ViewSet para los materiales de los cursos.
    """
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = [IsAuthenticated]


class ExamViewSet(viewsets.ModelViewSet):
    """
    API ViewSet para los exámenes.
    """
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]


class CrearExamenView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Vista para crear un examen.
    """
    template_name = 'exam/crear_examen.html'

    def test_func(self):
        """
        Verifica si el usuario es un superusuario o un instructor.
        """
        return self.request.user.is_superuser or self.request.user.role == 'instructor'

    def handle_no_permission(self):
        """
        Maneja el caso en el que el usuario no tiene permisos para crear el examen.
        """
        return render(self.request, '404.html')

    def get(self, request, course_id):
        """
        Maneja la solicitud GET para mostrar el formulario de creación de exámenes.
        """
        course = get_object_or_404(Course, id=course_id)
        exam_form = ExamForm()
        return render(request, self.template_name, {
            'course': course,
            'exam_form': exam_form
        })

    def post(self, request, course_id):
        """
        Maneja la solicitud POST para crear un nuevo examen.
        """
        course = get_object_or_404(Course, id=course_id)
        exam_form = ExamForm(request.POST)

        if exam_form.is_valid():
            exam = exam_form.save(commit=False)
            exam.course = course
            exam.save()

            # Lógica para agregar preguntas al examen
            question_texts = request.POST.getlist('question_text')
            question_types = request.POST.getlist('question_type')
            option1s = request.POST.getlist('option1')
            option2s = request.POST.getlist('option2')
            option3s = request.POST.getlist('option3')
            option4s = request.POST.getlist('option4')
            option5s = request.POST.getlist('option5')
            correct_options = request.POST.getlist('correct_option')

            for i, question_text in enumerate(question_texts):
                question = Question.objects.create(
                    exam=exam,
                    text=question_text,
                    question_type=question_types[i]
                )

                if question.question_type == 'multiple_choice':
                    options = [option1s[i], option2s[i], option3s[i], option4s[i], option5s[i]]
                    for j, option_text in enumerate(options):
                        if option_text:
                            is_correct = (j + 1) == int(correct_options[i])
                            Answer.objects.create(question=question, text=option_text, is_correct=is_correct)

            messages.success(request, 'Examen y preguntas creados exitosamente.')
            return redirect('course_detail', pk=course_id)
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
            return render(request, self.template_name, {
                'course': course,
                'exam_form': exam_form
            })


class ExamUpdateView(UpdateView):
    """
    Vista para actualizar un examen.
    """
    model = Exam
    fields = ['title', 'total_marks']
    template_name = 'exam/exam_edit.html'
    success_url = reverse_lazy('index')


class QuestionView(View):
    """
    Vista para mostrar una pregunta de un examen.
    """
    template_name = 'question/question_detail.html'

    def get_question(self, exam, question_number):
        """
        Obtiene una pregunta específica del examen.
        """
        questions = exam.questions.all()
        if question_number < 1 or question_number > len(questions):
            return None
        return questions[question_number - 1]

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        """
        Maneja la solicitud GET para mostrar una pregunta.
        """
        exam = get_object_or_404(Exam, pk=kwargs['exam_id'])
        question_number = kwargs.get('question_number', 1)
        question = self.get_question(exam, question_number)
        grade = Grade.objects.filter(student=request.user, exam=exam).first()

        if grade:
            # El examen ya fue tomado por el estudiante
            return redirect('exam_result', exam_id=exam.id)

        start_time = request.session.get(f'exam_{exam.id}_start_time')
        if not start_time:
            start_time = timezone.now()
            request.session[f'exam_{exam.id}_start_time'] = start_time.isoformat()

        remaining_time = exam.duration - (timezone.now() - start_time).seconds // 60
        if remaining_time <= 0:
            # El tiempo ha expirado
            return redirect('exam_result', exam_id=exam.id)

        form = AnswerForm(question=question)
        return render(request, self.template_name, {
            'exam': exam,
            'question': question,
            'question_number': question_number,
            'total_questions': exam.questions.count(),
            'form': form,
            'remaining_time': remaining_time,
        })

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        """
        Maneja la solicitud POST para responder una pregunta.
        """
        exam = get_object_or_404(Exam, pk=kwargs['exam_id'])
        question_number = kwargs.get('question_number', 1)
        question = self.get_question(exam, question_number)
        if not question:
            return redirect('exam_result', exam_id=exam.id)   

        form = AnswerForm(request.POST, question=question)
        if form.is_valid():
            selected_answer = get_object_or_404(Answer, id=form.cleaned_data['answer'])
            if selected_answer.is_correct:
                messages.success(request, '¡Correcto!')
            else:
                messages.error(request, '¡Incorrecto!')

            next_question_number = question_number + 1
            if next_question_number <= exam.questions.count():
                return redirect('question_detail', exam_id=exam.id, question_number=next_question_number)
            else:
                total_marks = self.calculate_marks(request.user, exam)
                Grade.objects.create(student=request.user, exam=exam, marks_obtained=total_marks)
                return redirect('exam_result', exam_id=exam.id)

        return render(request, self.template_name, {
            'exam': exam,
            'question': question,
            'question_number': question_number,
            'total_questions': exam.questions.count(),
            'form': form,
        })

    def calculate_marks(self, user, exam):
        """
        Calcula las calificaciones del usuario para un examen.
        """
        questions = exam.questions.all()
        marks_obtained = 0
        for question in questions:
            selected_answer = Answer.objects.filter(question=question, is_correct=True).first()
            if selected_answer:
                marks_obtained += 1
        return marks_obtained


class AnswerViewSet(viewsets.ModelViewSet):
    """
    API ViewSet para las respuestas de las preguntas de los exámenes.
    """
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = [IsAuthenticated]


class QuestionViewSet(viewsets.ModelViewSet):
    """
    API ViewSet para las preguntas de los exámenes.
    """
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class InstructorListView(LoginRequiredMixin, StudentAccessMixin, ListView):
    """
    Vista para listar los instructores.
    """
    model = User
    template_name = 'instructors/instructor_list.html'
    context_object_name = 'instructors'
    queryset = User.objects.filter(role='instructor')


class InstructorDetailView(LoginRequiredMixin, StudentAccessMixin, DetailView):
    """
    Vista para los detalles de un instructor.
    """
    model = User
    template_name = 'instructors/instructor_detail.html'
    context_object_name = 'instructor'


class InstructorCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Vista para crear un instructor.
    """
    model = User
    form_class = InstructorForm
    template_name = 'instructors/instructor_form.html'
    success_url = reverse_lazy('instructor_list')

    def test_func(self):
        """
        Verifica si el usuario es un superusuario.
        """
        return self.request.user.is_superuser

    def handle_no_permission(self):
        """
        Maneja el caso en el que el usuario no tiene permisos para crear un instructor.
        """
        return render(self.request, '404.html')

    def form_valid(self, form):
        """
        Establece el rol del usuario como 'instructor'.
        """
        form.instance.role = 'instructor'
        return super().form_valid(form)


class InstructorUpdateView(LoginRequiredMixin, StudentAccessMixin, UpdateView):
    """
    Vista para actualizar un instructor.
    """
    model = User
    form_class = InstructorForm
    template_name = 'instructors/instructor_form.html'
    success_url = reverse_lazy('instructor_list')

    def handle_no_permission(self):
        """
        Maneja el caso en el que el usuario no tiene permisos para actualizar el instructor.
        """
        return render(self.request, '404.html')


class InstructorDeleteView(LoginRequiredMixin, StudentAccessMixin, DeleteView):
    """
    Vista para eliminar un instructor.
    """
    model = User
    template_name = 'instructors/instructor_confirm_delete.html'
    success_url = reverse_lazy('instructor_list')

    def handle_no_permission(self):
        """
        Maneja el caso en el que el usuario no tiene permisos para eliminar el instructor.
        """
        return render(self.request, '404.html')


class InstructorLoginView(LoginView):
    """
    Vista para el inicio de sesión de instructores.
    """
    form_class = CustomAuthenticationForm
    template_name = 'accounts/instructor_login.html'

    def get_success_url(self):
        """
        Redirige al dashboard del instructor después de iniciar sesión.
        """
        return reverse('instructor_dashboard')


class AdminDashboardView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    """
    Vista para el dashboard del administrador.
    """
    template_name = 'admin/admin_dashboard.html'
    required_role = 'admin'

    def handle_no_permission(self):
        """
        Maneja el caso en el que el usuario no tiene permisos para acceder al dashboard del administrador.
        """
        return render(self.request, '404.html')


class InstructorDashboardView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    """
    Vista para el dashboard del instructor.
    """
    template_name = 'instructors/instructor_dashboard.html'
    required_role = 'instructor'

    def handle_no_permission(self):
        """
        Maneja el caso en el que el usuario no tiene permisos para acceder al dashboard del instructor.
        """
        return render(self.request, '404.html')


class StudentDashboardView(LoginRequiredMixin, TemplateView):
    """
    Vista para el dashboard del estudiante.
    """
    template_name = 'students/student_dashboard.html'

    def get_context_data(self, **kwargs):
        """
        Agrega los cursos en los que el estudiante está inscrito al contexto.
        """
        context = super().get_context_data(**kwargs)
        user = self.request.user
        enrolled_courses = Course.objects.filter(enrollment__student=user)
        context['enrolled_courses'] = enrolled_courses
        return context


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Vista para el dashboard principal.
    """
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        """
        Agrega los cursos al contexto según el rol del usuario.
        """
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.role == 'student':
            context['courses'] = Course.objects.filter(enrollment__student=user)
        else:
            context['courses'] = Course.objects.all()
        return context


@login_required
def enroll_course(request, pk):
    """
    Vista para inscribir a un usuario en un curso.
    """
    course = get_object_or_404(Course, pk=pk)
    user = request.user

    if user.role != 'student':
        return render(request, '404.html')

    if request.method == 'POST':
        enrollment, created = Enrollment.objects.get_or_create(student=user, course=course)
        if created:
            messages.success(request, f'Inscripción al curso "{course.title}" exitosa!')
        else:
            messages.info(request, f'Ya estás inscrito en el curso "{course.title}".')
        return redirect('course_detail', pk=course.pk)

    return render(request, 'course/enroll_confirm.html', {'course': course})


class AdminRequiredMixin(UserPassesTestMixin):
    """
    Mixin para verificar si el usuario es un administrador.
    """
    def test_func(self):
        """
        Verifica si el usuario es un administrador.
        """
        return self.request.user.is_authenticated and self.request.user.role == 'admin'

    def handle_no_permission(self):
        """
        Maneja el caso en el que el usuario no tiene permisos para acceder a la vista.
        """
        return render(self.request, '404.html')


def delete_all_enrollments(request):
    """
    Vista para eliminar todas las inscripciones.
    """
    Enrollment.objects.all().delete()
    return HttpResponse("All enrollments have been deleted.")


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_panel(request):
    """
    Vista para el panel de administración.
    """
    users = User.objects.all()
    groups = Group.objects.all()
    permissions = Permission.objects.all()

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        group_id = request.POST.get('group_id')
        action = request.POST.get('action')

        user = get_object_or_404(User, id=user_id)
        group = get_object_or_404(Group, id=group_id)

        if action == 'add':
            user.groups.add(group)
            messages.success(request, f'User {user.username} added to group {group.name}.')
        elif action == 'remove':
            user.groups.remove(group)
            messages.success(request, f'User {user.username} removed from group {group.name}.')

        return HttpResponseRedirect(reverse('admin_panel'))

    context = {
        'users': users,
        'groups': groups,
        'permissions': permissions
    }
    return render(request, 'accounts/user_management.html', context)


class CustomLoginView(LoginView):
    """
    Vista para el inicio de sesión personalizado.
    """
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    form_class = CustomAuthenticationForm

    def get_success_url(self):
        """
        Redirige al dashboard correspondiente según el rol del usuario después de iniciar sesión.
        """
        user = self.request.user
        if user.role == 'admin':
            return reverse('index')
        elif user.role == 'instructor':
            return reverse('instructor_dashboard')
        else:
            return reverse('student_dashboard')


class CustomLogoutView(View):
    """
    Vista para el cierre de sesión personalizado.
    """
    template_name = 'accounts/logout.html'

    def get(self, request, *args, **kwargs):
        """
        Maneja la solicitud GET para mostrar la página de cierre de sesión.
        """
        logout(request)
        return redirect('login')

    def post(self, request):
        """
        Maneja la solicitud POST para cerrar sesión.
        """
        logout(request)
        return redirect('login')


class ProfileView(LoginRequiredMixin, TemplateView):
    """
    Vista para el perfil del usuario.
    """
    template_name = 'accounts/perfil.html'

    def get(self, request, *args, **kwargs):
        """
        Maneja la solicitud GET para mostrar el formulario de perfil del usuario.
        """
        form = UserProfileForm(instance=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        """
        Maneja la solicitud POST para actualizar el perfil del usuario.
        """
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
        return render(request, self.template_name, {'form': form})


class SignupView(View):
    """
    Vista para el registro de nuevos usuarios.
    """
    def get(self, request):
        """
        Maneja la solicitud GET para mostrar el formulario de registro.
        """
        form = SignupForm()
        return render(request, 'accounts/signup.html', {'form': form})

    def post(self, request):
        """
        Maneja la solicitud POST para registrar un nuevo usuario.
        """
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        return render(request, 'accounts/signup.html', {'form': form})


class MyLoginView(View):
    """
    Vista personalizada para el inicio de sesión.
    """
    template_name = 'accounts/login.html'

    def get(self, request):
        """
        Maneja la solicitud GET para mostrar el formulario de inicio de sesión.
        """
        form = LoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        """
        Maneja la solicitud POST para autenticar al usuario.
        """
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('index')
            else:
                return render(request, self.template_name, {
                    'form': form,
                    'error_message': 'Usuario o contraseña incorrectos.'
                })
        return render(request, self.template_name, {'form': form})


class MyLogoutView(View):
    """
    Vista personalizada para el cierre de sesión.
    """
    template_name = 'accounts/logout.html'

    def get(self, request):
        """
        Maneja la solicitud GET para cerrar sesión.
        """
        logout(request)
        return redirect('login')

    def post(self, request):
        """
        Maneja la solicitud POST para cerrar sesión.
        """
        logout(request)
        return redirect('login')


class ExamDetailView(LoginRequiredMixin, DetailView):
    """
    Vista para los detalles de un examen.
    """
    model = Exam
    template_name = 'exam/exam_detail.html'
    context_object_name = 'exam'

    def get_context_data(self, **kwargs):
        """
        Agrega las preguntas del examen al contexto.
        """
        context = super().get_context_data(**kwargs)
        context['questions'] = self.object.questions.all()
        return context


class ExamResultView(View):
    """
    Vista para mostrar el resultado de un examen.
    """
    template_name = 'exam/exam_result.html'

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        """
        Maneja la solicitud GET para mostrar el resultado del examen.
        """
        exam = get_object_or_404(Exam, pk=kwargs['exam_id'])  
        grades = Grade.objects.filter(student=request.user, exam=exam)

        if not grades.exists():
            messages.error(request, 'No se ha encontrado el resultado del examen.')
            return redirect('exam_detail', pk=exam.id) 

        return render(request, self.template_name, {
            'exam': exam,
            'grades': grades,
        })


class ExamResultsView(LoginRequiredMixin, ListView):
    """
    Vista para listar los resultados de los exámenes del usuario.
    """
    template_name = 'exam/exam_result.html'
    context_object_name = 'grades'

    def get_queryset(self):
        """
        Devuelve las calificaciones del estudiante.
        """
        return Grade.objects.filter(student=self.request.user)


class ExamDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Vista para eliminar un examen.
    """
    model = Exam
    template_name = 'exam/exam_confirm_delete.html'
    success_url = reverse_lazy('course_list')

    def test_func(self):
        """
        Verifica si el usuario tiene permisos para eliminar el examen.
        """
        exam = self.get_object()
        return self.request.user.is_superuser or (self.request.user.role == 'instructor' and exam.course.instructor == self.request.user)

    def handle_no_permission(self):
        """
        Maneja el caso en el que el usuario no tiene permisos para eliminar el examen.
        """
        return render(self.request, '404.html')

    def delete(self, request, *args, **kwargs):
        """
        Maneja la solicitud de eliminación del examen.
        """
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        messages.success(request, 'Examen eliminado exitosamente.')
        return redirect(success_url)


class ForumListView(ListView):
    """
    Vista para listar los foros de un curso.
    """
    model = Forum
    template_name = 'forum/forum_list.html'
    context_object_name = 'forums'

    def get_queryset(self):
        """
        Devuelve los foros de un curso específico.
        """
        course_id = self.kwargs['course_id']
        return Forum.objects.filter(course_id=course_id)

    def get_context_data(self, **kwargs):
        """
        Agrega el curso al contexto.
        """
        context = super().get_context_data(**kwargs)
        context['course'] = get_object_or_404(Course, pk=self.kwargs['course_id'])
        return context


class InstructorRequiredMixin(UserPassesTestMixin):
    """
    Mixin para verificar si el usuario es un instructor.
    """
    def test_func(self):
        """
        Verifica si el usuario es un instructor.
        """
        return self.request.user.is_authenticated and self.request.user.role == 'instructor'
    def handle_no_permission(self):
        """
        Maneja el caso en el que el usuario no tiene permisos para acceder a la vista.
        """
        return render(self.request, '404.html')  


class ForumCreateView(LoginRequiredMixin, InstructorRequiredMixin, CreateView):
    """
    Vista para crear un foro.
    """
    model = Forum
    form_class = ForumForm
    template_name = 'forum/forum_form.html'

    def form_valid(self, form):
        """
        Establece el curso y el creador del foro.
        """
        form.instance.course = get_object_or_404(Course, pk=self.kwargs['course_id'])
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """
        Redirige a la lista de foros después de crear el foro.
        """
        return reverse_lazy('forum_list', kwargs={'course_id': self.kwargs['course_id']})

    def get_context_data(self, **kwargs):
        """
        Agrega el ID del curso al contexto.
        """
        context = super().get_context_data(**kwargs)
        context['course_id'] = self.kwargs['course_id']
        return context


class ForumDetailView(DetailView):
    """
    Vista para los detalles de un foro.
    """
    model = Forum
    template_name = 'forum/forum_detail.html'
    context_object_name = 'forum'

    def get_context_data(self, **kwargs):
        """
        Agrega las publicaciones del foro al contexto.
        """
        context = super().get_context_data(**kwargs)
        context['posts'] = Post.objects.filter(forum=self.object)
        context['post_form'] = PostForm()
        return context

    def post(self, request, *args, **kwargs):
        """
        Maneja la solicitud POST para agregar una nueva publicación al foro.
        """
        self.object = self.get_object()
        post_form = PostForm(request.POST)

        if post_form.is_valid():
            post = post_form.save(commit=False)
            post.forum = self.object
            post.created_by = request.user
            post.save()
            return redirect('forum_detail', pk=self.object.pk)
        
        context = self.get_context_data(object=self.object)
        context['post_form'] = post_form
        return self.render_to_response(context)


class PostCreateView(CreateView):
    """
    Vista para crear una publicación en un foro.
    """
    model = Post
    form_class = PostForm
    template_name = 'forum/post_form.html'

    def form_valid(self, form):
        """
        Establece el foro y el creador de la publicación.
        """
        form.instance.forum = get_object_or_404(Forum, pk=self.kwargs['forum_id'])
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """
        Redirige a los detalles del foro después de crear la publicación.
        """
        return reverse('forum_detail', kwargs={'pk': self.kwargs['forum_id']})
