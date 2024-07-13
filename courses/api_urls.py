# api_urls.py
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, MaterialViewSet, ExamViewSet, QuestionViewSet, AnswerViewSet

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'materials', MaterialViewSet)
router.register(r'exams', ExamViewSet)
router.register(r'questions', QuestionViewSet)
router.register(r'answers', AnswerViewSet)

urlpatterns = router.urls
