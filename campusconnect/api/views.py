from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404

from accounts.models import User
from academics.models import Course, Enrollment, LectureMaterial, Assignment, Submission
from .serializers import (
    RegisterSerializer, UserSerializer,
    CourseSerializer, AssignmentSerializer,
    SubmissionSerializer, LectureMaterialSerializer
)

# ---------------- AUTH ---------------- #

class RegisterAPIView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def login_api(request):
    username = request.data.get("username")
    password = request.data.get("password")
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return Response({"message": "Logged in", "user": UserSerializer(user).data})
    return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
def logout_api(request):
    logout(request)
    return Response({"message": "Logged out"})

@api_view(["GET"])
def me_api(request):
    return Response(UserSerializer(request.user).data)

# ---------------- COURSES ---------------- #

class CourseListAPI(generics.ListAPIView):
    queryset = Course.objects.all().select_related("teacher")
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def enroll_api(request, pk):
    if request.user.role != "STUDENT":
        return Response({"detail": "Only students can enroll."}, status=status.HTTP_403_FORBIDDEN)
    course = get_object_or_404(Course, pk=pk)
    Enrollment.objects.get_or_create(course=course, student=request.user)
    return Response({"message": "Enrolled successfully"})

# ---------------- MATERIALS ---------------- #

class CourseMaterialsAPI(generics.ListCreateAPIView):
    serializer_class = LectureMaterialSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return LectureMaterial.objects.filter(course_id=self.kwargs["pk"])

    def perform_create(self, serializer):
        course = get_object_or_404(Course, pk=self.kwargs["pk"])
        if self.request.user.role != "TEACHER" or course.teacher_id != self.request.user.id:
            raise permissions.PermissionDenied("Not your course.")
        serializer.save(course=course, uploaded_by=self.request.user)

# ---------------- ASSIGNMENTS ---------------- #

class CourseAssignmentsAPI(generics.ListCreateAPIView):
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Assignment.objects.filter(course_id=self.kwargs["pk"])

    def perform_create(self, serializer):
        course = get_object_or_404(Course, pk=self.kwargs["pk"])
        if self.request.user.role != "TEACHER" or course.teacher_id != self.request.user.id:
            raise permissions.PermissionDenied("Not your course.")
        serializer.save(course=course)

@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def submit_assignment_api(request, pk):
    if request.user.role != "STUDENT":
        return Response({"detail": "Only students can submit."}, status=status.HTTP_403_FORBIDDEN)

    asg = get_object_or_404(Assignment, pk=pk)

    # check enrollment
    if not Enrollment.objects.filter(course=asg.course, student=request.user).exists():
        return Response({"detail": "Enroll first."}, status=status.HTTP_403_FORBIDDEN)

    sub, _ = Submission.objects.get_or_create(assignment=asg, student=request.user)
    if "file" not in request.FILES:
        return Response({"detail": "File is required"}, status=status.HTTP_400_BAD_REQUEST)

    sub.file = request.FILES["file"]
    sub.save()
    return Response(SubmissionSerializer(sub).data)

@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def grade_submission_api(request, pk):
    if request.user.role != "TEACHER":
        return Response({"detail": "Only teachers can grade."}, status=status.HTTP_403_FORBIDDEN)

    sub = get_object_or_404(Submission, pk=pk, assignment__course__teacher=request.user)
    sub.grade = request.data.get("grade")
    sub.feedback = request.data.get("feedback", "")
    sub.save()
    return Response({"message": "Graded successfully"})
