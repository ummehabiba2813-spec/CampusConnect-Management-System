from rest_framework import serializers
from accounts.models import User
from academics.models import Course, LectureMaterial, Assignment, Submission

# --- Accounts ---
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "email_verified", "first_name", "last_name"]

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "role", "password"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

# --- Academics ---
class CourseSerializer(serializers.ModelSerializer):
    teacher_name = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ["id", "code", "title", "description", "teacher", "teacher_name"]

    def get_teacher_name(self, obj):
        return getattr(obj.teacher, "username", None)

class AssignmentSerializer(serializers.ModelSerializer):
    course_code = serializers.ReadOnlyField(source="course.code")

    class Meta:
        model = Assignment
        fields = ["id", "course", "course_code", "title", "description", "due_at"]

class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ["id", "assignment", "student", "file", "submitted_at", "grade", "feedback"]
        read_only_fields = ["student", "submitted_at", "grade", "feedback"]

class LectureMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = LectureMaterial
        fields = ["id", "course", "title", "file", "file_type", "uploaded_at", "uploaded_by"]
        read_only_fields = ["uploaded_at", "uploaded_by"]
