from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from rest_framework import viewsets
from django.contrib.auth.decorators import login_required, user_passes_test
from rest_framework.permissions import IsAuthenticated
from django.urls import reverse_lazy, reverse
from django.contrib.auth.views import LoginView 
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from .forms import ExamForm, ForumForm, PostForm,   UserProfileForm, CourseForm, InstructorForm, CustomAuthenticationForm, MaterialForm, SignupForm, LoginForm, AnswerForm
from .models import Course, Enrollment, Forum, Material, Exam, Post, Question, Answer, Grade, User
from .serializers import CourseSerializer, MaterialSerializer, ExamSerializer, QuestionSerializer, AnswerSerializer
from django.contrib.auth.models import Group, Permission
 
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator


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
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['courses'] = Course.objects.all()
        context['exams'] = Exam.objects.all()
        context['enrolled_courses'] = self.get_user_courses()
        return context


class CourseListView(LoginRequiredMixin, StudentAccessMixin, ListView, StudentCheckMixin):
    model = Course
    template_name = 'course/course_list.html'
    context_object_name = 'courses'

    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            return Course.objects.filter(enrollment__student=user)
        return Course.objects.all()


class CourseDetailView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'course/course_detail.html'
    context_object_name = 'course'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        user = request.user
        if user.role == 'student' and not Enrollment.objects.filter(student=user, course=self.object).exists():
            messages.error(request, 'Debes inscribirte en el curso para verlo.')
            return redirect('enroll_course', pk=self.object.pk)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['exams'] = self.object.exams.all()
        context['back_url'] = reverse('student_dashboard') if self.request.user.role == 'student' else reverse('course_list')
        return context


class CourseCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'course/course_form.html'
    success_url = reverse_lazy('course_list')

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role == 'instructor'

    def handle_no_permission(self):
        return render(self.request, '404.html')


class CourseUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'course/course_form.html'
    success_url = reverse_lazy('course_list')

    def test_func(self):
        course = self.get_object()
        return self.request.user.is_superuser or (self.request.user.role == 'instructor' and course.instructor == self.request.user)

    def handle_no_permission(self):
        return render(self.request, '404.html')


class CourseDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Course
    template_name = 'course/course_confirm_delete.html'
    success_url = reverse_lazy('course_list')

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role == 'instructor'

    def handle_no_permission(self):
        return render(self.request, '404.html')


class MaterialListView(LoginRequiredMixin, StudentAccessMixin, ListView):
    model = Material
    template_name = 'material/material_list.html'
    context_object_name = 'materials'

    def get_queryset(self):
        user = self.request.user
        if user.role == 'instructor':
            return Material.objects.filter(course__instructor=user)
        return Material.objects.none()


class MaterialDetailView(LoginRequiredMixin, StudentAccessMixin, UserPassesTestMixin, DetailView):
    model = Material
    template_name = 'material/material_detail.html'
    context_object_name = 'material'

    def test_func(self):
        material = self.get_object()
        return self.request.user == material.course.instructor or self.request.user.is_superuser

    def handle_no_permission(self):
        return render(self.request, '404.html')


class MaterialCreateView(LoginRequiredMixin, StudentAccessMixin, UserPassesTestMixin, CreateView):
    model = Material
    form_class = MaterialForm
    template_name = 'material/material_form.html'
    success_url = reverse_lazy('material_list')

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role == 'instructor'

    def handle_no_permission(self):
        return render(self.request, '404.html')


class MaterialUpdateView(LoginRequiredMixin, StudentAccessMixin, UserPassesTestMixin, UpdateView):
    model = Material
    form_class = MaterialForm
    template_name = 'material/material_form.html'
    success_url = reverse_lazy('material_list')

    def test_func(self):
        material = self.get_object()
        return self.request.user.is_superuser or (self.request.user.role == 'instructor' and material.course.instructor == self.request.user)

    def handle_no_permission(self):
        return render(self.request, '404.html')


class MaterialDeleteView(LoginRequiredMixin, StudentAccessMixin, UserPassesTestMixin, DeleteView):
    model = Material
    template_name = 'material/material_confirm_delete.html'
    success_url = reverse_lazy('material_list')

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role == 'instructor'

    def handle_no_permission(self):
        return render(self.request, '404.html')


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]


class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = [IsAuthenticated]


class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]


class CrearExamenView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'exam/crear_examen.html'

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role == 'instructor'

    def handle_no_permission(self):
        return render(self.request, '404.html')

    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        exam_form = ExamForm()
        return render(request, self.template_name, {
            'course': course,
            'exam_form': exam_form
        })

    def post(self, request, course_id):
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
    model = Exam
    fields = ['title', 'total_marks']
    template_name = 'exam/exam_edit.html'
    success_url = reverse_lazy('index')
                
            
class QuestionView(View):
    template_name = 'question/question_detail.html'

    def get_question(self, exam, question_number):
        questions = exam.questions.all()
        if question_number < 1 or question_number > len(questions):
            return None
        return questions[question_number - 1]

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        exam = get_object_or_404(Exam, pk=kwargs['exam_id'])
        question_number = kwargs.get('question_number', 1)
        question = self.get_question(exam, question_number)
        if not question:
            return redirect('exam_result', exam_id=exam.id)   

        form = AnswerForm(question=question)
        return render(request, self.template_name, {
            'exam': exam,
            'question': question,
            'question_number': question_number,
            'total_questions': exam.questions.count(),
            'form': form,
        })

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
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
        questions = exam.questions.all()
        marks_obtained = 0
        for question in questions:
            selected_answer = Answer.objects.filter(question=question, is_correct=True).first()
            if selected_answer:
                marks_obtained += 1
        return marks_obtained


 

class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = [IsAuthenticated]


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class InstructorListView(LoginRequiredMixin, StudentAccessMixin, ListView):
    model = User
    template_name = 'instructors/instructor_list.html'
    context_object_name = 'instructors'
    queryset = User.objects.filter(role='instructor')


class InstructorDetailView(LoginRequiredMixin, StudentAccessMixin, DetailView):
    model = User
    template_name = 'instructors/instructor_detail.html'
    context_object_name = 'instructor'


class InstructorCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = User
    form_class = InstructorForm
    template_name = 'instructors/instructor_form.html'
    success_url = reverse_lazy('instructor_list')

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return render(self.request, '404.html')

    def form_valid(self, form):
        form.instance.role = 'instructor'
        return super().form_valid(form)


class InstructorUpdateView(LoginRequiredMixin, StudentAccessMixin, UpdateView):
    model = User
    form_class = InstructorForm
    template_name = 'instructors/instructor_form.html'
    success_url = reverse_lazy('instructor_list')

    def handle_no_permission(self):
        return render(self.request, '404.html')


class InstructorDeleteView(LoginRequiredMixin, StudentAccessMixin, DeleteView):
    model = User
    template_name = 'instructors/instructor_confirm_delete.html'
    success_url = reverse_lazy('instructor_list')

    def handle_no_permission(self):
        return render(self.request, '404.html')


class InstructorLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'accounts/instructor_login.html'

    def get_success_url(self):
        return reverse('instructor_dashboard')


class AdminDashboardView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    template_name = 'admin/admin_dashboard.html'
    required_role = 'admin'

    def handle_no_permission(self):
        return render(self.request, '404.html')


class InstructorDashboardView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    template_name = 'instructors/instructor_dashboard.html'
    required_role = 'instructor'

    def handle_no_permission(self):
        return render(self.request, '404.html')


class StudentDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'students/student_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        enrolled_courses = Course.objects.filter(enrollment__student=user)
        context['enrolled_courses'] = enrolled_courses
        return context


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.role == 'student':
            context['courses'] = Course.objects.filter(enrollment__student=user)
        else:
            context['courses'] = Course.objects.all()
        return context


@login_required
def enroll_course(request, pk):
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
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'admin'

    def handle_no_permission(self):
        return render(self.request, '404.html')


def delete_all_enrollments(request):
    Enrollment.objects.all().delete()
    return HttpResponse("All enrollments have been deleted.")


 

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_panel(request):
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
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    form_class = CustomAuthenticationForm

    def get_success_url(self):
        user = self.request.user
        if user.role == 'admin':
            return reverse('index')
        elif user.role == 'instructor':
            return reverse('instructor_dashboard')
        else:
            return reverse('student_dashboard')


class CustomLogoutView(View):
    template_name = 'accounts/logout.html'

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('login')

    def post(self, request):
        logout(request)
        return redirect('login')


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/perfil.html'

    def get(self, request, *args, **kwargs):
        form = UserProfileForm(instance=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
        return render(request, self.template_name, {'form': form})


class SignupView(View):
    def get(self, request):
        form = SignupForm()
        return render(request, 'accounts/signup.html', {'form': form})

    def post(self, request):
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        return render(request, 'accounts/signup.html', {'form': form})


class MyLoginView(View):
    template_name = 'accounts/login.html'

    def get(self, request):
        form = LoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
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
    template_name = 'accounts/logout.html'

    def get(self, request):
        logout(request)
        return redirect('login')

    def post(self, request):
        logout(request)
        return redirect('login')


class ExamDetailView(LoginRequiredMixin, DetailView):
    model = Exam
    template_name = 'exam/exam_detail.html'
    context_object_name = 'exam'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['questions'] = self.object.questions.all()
        return context



class ExamResultView(View):
    template_name = 'exam/exam_result.html'

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        exam = get_object_or_404(Exam, pk=kwargs['exam_id'])  
        grades = Grade.objects.filter(student=request.user, exam=exam)

        if not grades.exists():
            messages.error(request, 'No se ha encontrado el resultado del examen.')
            return redirect('exam_detail', pk=exam.id) 

        return render(request, self.template_name, {
            'exam': exam,
            'grades': grades,
        })


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

# Clases ForumView
class ForumListView(ListView):
    model = Forum
    template_name = 'forum/forum_list.html'
    context_object_name = 'forums'

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        return Forum.objects.filter(course_id=course_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = get_object_or_404(Course, pk=self.kwargs['course_id'])
        return context

class InstructorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'instructor'

    def handle_no_permission(self):
        return render(self.request, '404.html')  
    

class ForumCreateView(LoginRequiredMixin, InstructorRequiredMixin, CreateView):
    model = Forum
    form_class = ForumForm
    template_name = 'forum/forum_form.html'

    def form_valid(self, form):
        form.instance.course = get_object_or_404(Course, pk=self.kwargs['course_id'])
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('forum_list', kwargs={'course_id': self.kwargs['course_id']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course_id'] = self.kwargs['course_id']
        return context


class ForumDetailView(DetailView):
    model = Forum
    template_name = 'forum/forum_detail.html'
    context_object_name = 'forum'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = Post.objects.filter(forum=self.object)
        context['post_form'] = PostForm()
        return context

    def post(self, request, *args, **kwargs):
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
    model = Post
    form_class = PostForm
    template_name = 'forum/post_form.html'

    def form_valid(self, form):
        form.instance.forum = get_object_or_404(Forum, pk=self.kwargs['forum_id'])
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('forum/forum_detail', kwargs={'forum_id': self.kwargs['forum_id']})
