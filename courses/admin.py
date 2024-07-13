from django.contrib import admin
from .models import User, Course, Material, Enrollment, Exam, Question, Answer, Grade, Forum, Post

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'email')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'start_date', 'end_date')
    search_fields = ('title', 'description')
    list_filter = ('start_date', 'end_date', 'instructor')

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'file_type', 'uploaded_at')
    list_filter = ('course', 'file_type')
    search_fields = ('title',)

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrollment_date')
    list_filter = ('course', 'enrollment_date')
    search_fields = ('student__username', 'course__title')

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'total_marks')
    list_filter = ('course',)
    search_fields = ('title', 'course__title')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'exam', 'question_type')
    list_filter = ('exam', 'question_type')
    search_fields = ('text', 'exam__title')

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'is_correct')
    list_filter = ('question', 'is_correct')
    search_fields = ('text', 'question__text')

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'marks_obtained')
    list_filter = ('exam',)
    search_fields = ('student__username', 'exam__title')

@admin.register(Forum)
class ForumAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'created_at', 'created_by')
    list_filter = ('course', 'created_at')
    search_fields = ('title', 'course__title', 'created_by__username')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('forum', 'content', 'created_at', 'created_by')
    list_filter = ('forum', 'created_at')
    search_fields = ('content', 'forum__title', 'created_by__username')
