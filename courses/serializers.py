from rest_framework import serializers
from .models import Course, Material, Exam, Question, Answer, Enrollment, User

class MaterialSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Material.
    Serializa todos los campos del modelo.
    """
    class Meta:
        model = Material
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Question.
    Serializa todos los campos del modelo.
    """
    class Meta:
        model = Question
        fields = '__all__'

class AnswerSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Answer.
    Serializa todos los campos del modelo.
    """
    class Meta:
        model = Answer
        fields = '__all__'

class ExamSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Exam.
    Incluye una relación anidada con QuestionSerializer para serializar las preguntas asociadas.
    """
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Exam
        fields = ['id', 'title', 'course', 'total_marks', 'questions']

class CourseSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Course.
    Incluye relaciones anidadas con MaterialSerializer y ExamSerializer para serializar los materiales y exámenes asociados.
    """
    materials = MaterialSerializer(many=True, read_only=True)
    exams = ExamSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'start_date', 'end_date', 'instructor', 'materials', 'exams']

    def validate_end_date(self, value):
        """
        Validación para asegurarse de que la fecha de finalización no sea anterior a la fecha de inicio.
        """
        start_date = self.initial_data.get('start_date')
        if start_date and value < start_date:
            raise serializers.ValidationError("La fecha de finalización no puede ser anterior a la fecha de inicio.")
        return value

class EnrollmentSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Enrollment.
    Serializa todos los campos del modelo.
    """
    class Meta:
        model = Enrollment
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo User.
    Serializa los campos id, username, email y role del modelo.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']
