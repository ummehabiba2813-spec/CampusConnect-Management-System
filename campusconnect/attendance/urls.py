from django.urls import path
from . import views

urlpatterns = [
     path("create/", views.create_attendance_sheet, name="create_attendance_sheet"),
    path("get_teachers/", views.get_teachers_by_session, name="get_teachers_by_session"),  # new
    path("attendance/manage/", views.manage_attendance, name="manage_attendance"),
    path("get_students/", views.get_students, name="get_students"),
        path("teacher/attendance/mark/<int:sheet_id>/", views.mark_attendance, name="mark_attendance"),
        path("student_attendance/", views.student_attendance, name="student_attendance"),


]
