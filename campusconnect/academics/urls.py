from django.urls import path
from . import views
from .views import (
    CourseListView, CourseDetailView, CourseCreateView, CourseUpdateView, CourseDeleteView,
    enroll_course, unenroll_course, upload_material,
    create_assignment, create_submission, assignment_submissions, grade_submission
)

urlpatterns = [
     # Assignments & Submissions
    path("assignments/create/", views.create_assignment, name="create_assignment"),
    path("create/", views.create_assignment, name="create_assignment"),
    path("assignments/manage/", views.manage_assignments, name="manage_assignments"),
    path("assignments/<int:assignment_pk>/submit/", create_submission, name="submission-create"),
    path("submissions/<int:submission_pk>/grade/", grade_submission, name="submission-grade"),
    path('assignments/<int:assignment_id>/delete/', views.delete_assignment_confirm, name='delete_assignment_confirm'),
    path('assignments/<int:assignment_id>/delete/confirm/', views.delete_assignment, name='delete_assignment'),
    path('assignments/edit/<int:assignment_id>/', views.edit_assignment, name='edit_assignment'),
         # Assignments & Submissions for student

path('assignment/<int:assignment_id>/submissions/', views.assignment_submissions, name='assignment_submissions'),
    path('submit-assignment/<int:assignment_id>/', views.submit_assignment_view, name='submit_assignment'),
    # Courses
    path("courses/", CourseListView.as_view(), name="course-list"),
    path("courses/create/", CourseCreateView.as_view(), name="course-create"),
    path("courses/<int:pk>/", CourseDetailView.as_view(), name="course-detail"),
    

    # Enrollment
    path('my-courses/', views.student_courses, name='student_courses'),

    path("courses/<int:pk>/enroll/", enroll_course, name="course-enroll"),
    path("courses/<int:pk>/unenroll/", unenroll_course, name="course-unenroll"),
    path("manage/", views.manage_courses, name="manage_courses"),
    path("edit/<int:course_id>/", views.edit_course, name="edit_course"),
    path("delete/<int:course_id>/", views.delete_course, name="delete_course"),  # 👈 ye wala
    # Material
    path("courses/<int:course_pk>/materials/upload/", upload_material, name="upload_material"),

    # Course management
    path("add/", views.add_course, name="add_course"),
    # Departments
    path("departments/", views.manage_departments, name="manage_departments"),
    path("departments/add/", views.add_department, name="add_department"),
    path("departments/edit/<int:pk>/", views.edit_department, name="edit_department"),
    path("departments/delete/<int:pk>/", views.delete_department, name="delete_department"),


   


    # Teacher dashboard routes
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/submissions/grade/', grade_submission, name='grade_submissions'),
    path('teacher/courses/', views.teacher_courses, name='teacher_courses'),
]
