from django.urls import path
from . import views
from .views import ExamDeleteView, ExamDetailView, ExamResultView, ExamUpdateView, ExamViewSet, QuestionView,   SignupView, MyLoginView, MyLogoutView, CrearExamenView, admin_panel, delete_all_enrollments, ForumListView, ForumCreateView, ForumDetailView, PostCreateView
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings
from rest_framework.routers import DefaultRouter

# Creamos un enrutador para las vistas de API
router = DefaultRouter()
router.register(r'api/exam', ExamViewSet)
router.register(r'api/question', views.QuestionViewSet)
router.register(r'api/answer', views.AnswerViewSet)

urlpatterns = [
    # Rutas de cursos
    path('', views.IndexView.as_view(), name='index'),
    path('list/', views.CourseListView.as_view(), name='course_list'),
    path('add/', views.CourseCreateView.as_view(), name='agregar_curso'),
    path('<int:pk>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('<int:pk>/edit/', views.CourseUpdateView.as_view(), name='editar_curso'),
    path('<int:pk>/delete/', views.CourseDeleteView.as_view(), name='eliminar_curso'),
    path('<int:pk>/enroll/', views.enroll_course, name='enroll_course'),
    path('delete_all_enrollments/', delete_all_enrollments, name='delete_all_enrollments'),
    
    # Rutas de materiales
    path('materials/', views.MaterialListView.as_view(), name='material_list'),
    path('materials/add/', views.MaterialCreateView.as_view(), name='material_add'),
    path('materials/<int:pk>/', views.MaterialDetailView.as_view(), name='material_detail'),
    path('materials/<int:pk>/edit/', views.MaterialUpdateView.as_view(), name='material_edit'),
    path('materials/<int:pk>/delete/', views.MaterialDeleteView.as_view(), name='material_delete'),

    # Rutas de instructores
    path('instructors/', views.InstructorListView.as_view(), name='instructor_list'),
    path('instructors/add/', views.InstructorCreateView.as_view(), name='instructor_add'),
    path('instructors/<int:pk>/', views.InstructorDetailView.as_view(), name='instructor_detail'),
    path('instructors/<int:pk>/edit/', views.InstructorUpdateView.as_view(), name='instructor_edit'),
    path('instructors/<int:pk>/delete/', views.InstructorDeleteView.as_view(), name='instructor_delete'),

    # Rutas para el reseteo de contraseñas
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='accounts/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),

    # Rutas de autenticación
    path('accounts/signup/', SignupView.as_view(), name='signup'),
    path('accounts/login/', MyLoginView.as_view(), name='login'),
    path('accounts/logout/', MyLogoutView.as_view(), name='logout'),
    path('accounts/register/', SignupView.as_view(), name='register'),
    path('accounts/profile/', views.ProfileView.as_view(), name='profile'),
    path('admin_panel/', admin_panel, name='admin_panel'),

    # Rutas de dashboards
    path('admin/dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('instructors/dashboard/', views.InstructorDashboardView.as_view(), name='instructor_dashboard'),
    path('students/dashboard/', views.StudentDashboardView.as_view(), name='student_dashboard'),
    

    # Rutas para exámenes
    path('course/<int:course_id>/exam/create/', CrearExamenView.as_view(), name='crear_examen'),
    path('exam/<int:pk>/delete/', ExamDeleteView.as_view(), name='exam_delete'),
    path('exam/<int:pk>/', ExamDetailView.as_view(), name='exam_detail'),
    path('exam/<int:exam_id>/result/', ExamResultView.as_view(), name='exam_result'),
    path('exam/<int:exam_id>/question/<int:question_number>/', QuestionView.as_view(), name='question_detail'),
    path('exam/<int:pk>/edit/', ExamUpdateView.as_view(), name='exam_edit'),
 
 
 
    
    # Rutas para foros
    path('course/<int:course_id>/foros/', ForumListView.as_view(), name='forum_list'),
    path('course/<int:course_id>/foros/crear/', ForumCreateView.as_view(), name='forum_create'),
    path('forum/<int:pk>/', ForumDetailView.as_view(), name='forum_detail'),
    path('forum/<int:forum_id>/crear_post/', PostCreateView.as_view(), name='post_create'),
]

# Añadir las rutas del enrutador de DRF
urlpatterns += router.urls

# Añadir soporte para archivos estáticos en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
