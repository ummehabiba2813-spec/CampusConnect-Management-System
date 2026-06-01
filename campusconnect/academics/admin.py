from django.contrib import admin
from django.contrib import admin
from .models import Attendance
from .models import (
    Department, Course, Enrollment, ClassSession,
    Announcement, Assignment, Submission, Attendance,
    LectureMaterial
)

# academics/admin.py
from django.contrib import admin
from .models import Timetable

admin.site.register(Timetable)
# ---------------- Department ----------------
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("code", "name")
    search_fields = ("code", "name")

# ---------------- Course ----------------
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        'code',
        'title',
        'department',
        'class_name',
        'teacher_name',
        'teacher_id',
    )

    list_filter = (
        'department',
        'class_name',
    )


# ---------------- Enrollment ----------------
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("course", "student", "created_at")
    list_filter = ("course",)

# ---------------- ClassSession ----------------
@admin.register(ClassSession)
class ClassSessionAdmin(admin.ModelAdmin):
    list_display = ("course", "topic", "start_time", "end_time", "room")
    list_filter = ("course",)
    search_fields = ("topic",)

# ---------------- Announcement ----------------

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "created_by", "created_at")  # removed 'course'
    list_filter = ("created_by", "created_at")             # removed 'course'
    search_fields = ("title", "body", "created_by")

# ---------------- Assignment ----------------
@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "description", "due_at", "created_by")  # course hata diya
    list_filter = ("due_at", "class_name", "section")  # course hata diya
    search_fields = ("title", "description")


# ---------------- Submission ----------------
@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("assignment", "student", "submitted_at", "grade")
    list_filter = ("assignment",)

# ---------------- Attendance ----------------

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'status', 'created_at')  # changed 'date' -> 'created_at'
    list_filter = ('status', 'created_at')  # changed 'date' -> 'created_at'
    search_fields = ('student__username', 'course__code')

# ---------------- LectureMaterial ----------------
@admin.register(LectureMaterial)
class LectureMaterialAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "file_type", "uploaded_by", "uploaded_at")
    list_filter = ("file_type", "course")
    search_fields = ("title",)
