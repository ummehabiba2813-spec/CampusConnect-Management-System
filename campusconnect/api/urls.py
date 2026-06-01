from django.urls import path
from .views import (
    RegisterAPIView, login_api, logout_api, me_api,
    CourseListAPI, enroll_api, CourseMaterialsAPI, CourseAssignmentsAPI,
    submit_assignment_api, grade_submission_api
)

urlpatterns = [
    # Auth
    path("auth/register/", RegisterAPIView.as_view(), name="api-register"),
    path("auth/login/", login_api, name="api-login"),
    path("auth/logout/", logout_api, name="api-logout"),
    path("auth/me/", me_api, name="api-me"),

    # Courses
    path("courses/", CourseListAPI.as_view(), name="course-list"),
    path("courses/<int:pk>/enroll/", enroll_api, name="course-enroll"),
    path("courses/<int:pk>/materials/", CourseMaterialsAPI.as_view(), name="course-materials"),
    path("courses/<int:pk>/assignments/", CourseAssignmentsAPI.as_view(), name="course-assignments"),

    # Assignments / Submissions
    path("assignments/<int:pk>/submit/", submit_assignment_api, name="assignment-submit"),
    path("submissions/<int:pk>/grade/", grade_submission_api, name="submission-grade"),
]
