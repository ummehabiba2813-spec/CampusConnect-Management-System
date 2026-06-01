from django.utils import timezone
from django.db.models import Count, Q, Avg
from .models import Course, ClassSession, Announcement, Assignment, Submission, Attendance
from accounts.models import User

# ===================== Student Dashboard =====================


def student_dashboard(user, limit=5):
    now = timezone.now()

    # Courses the student is enrolled in
    enrolled_courses_qs = Course.objects.filter(enrollments__student=user)

    # Upcoming classes
    upcoming_classes = (
        ClassSession.objects
        .filter(course__in=enrolled_courses_qs, start_time__gte=now)
        .select_related("course")
        .order_by("start_time")[:limit]
    )

    # Announcements
    announcements = Announcement.objects.order_by("-created_at")[:limit]

    # Teachers of enrolled courses (as integer IDs)
    teacher_ids = enrolled_courses_qs.values_list('teacher_id', flat=True)

    # Pending assignments created by teachers of enrolled courses
    pending_assignments = (
        Assignment.objects
        .filter(
            created_by__role='teacher',
            created_by_id__in=teacher_ids,
            due_at__gte=now
        )
        .exclude(submissions__student=user)
        .select_related("created_by")  # teacher info
        .order_by("due_at")[:limit]
    )

    # Attendance stats
    total_sessions = Attendance.objects.filter(student=user).count()
    present_sessions = Attendance.objects.filter(student=user, status=Attendance.PRESENT).count()
    attendance_pct = round((present_sessions / total_sessions) * 100, 1) if total_sessions else 0.0

    # Average grade
    avg_grade = (
        Submission.objects.filter(student=user, grade__isnull=False)
        .aggregate(avg=Avg("grade"))["avg"] or 0
    )

    return {
        "upcoming_classes": upcoming_classes,
        "announcements": announcements,
        "pending_assignments": pending_assignments,
        "stats": {
            "attendance_pct": attendance_pct,
            "avg_grade": float(avg_grade),
            "pending_count": pending_assignments.count(),
        },
    }

# ===================== Teacher Dashboard =====================
from django.utils import timezone
from accounts.models import User
from .models import Course, ClassSession, Submission

def teacher_dashboard(user, limit=5):
    now = timezone.now()
    my_courses = Course.objects.filter(teacher=user)

    upcoming_classes = ClassSession.objects.filter(
        course__in=my_courses,
        start_time__gte=now
    ).select_related("course").order_by("start_time")[:limit]

    assignments_to_grade = Submission.objects.filter(
        assignment__course__in=my_courses,
        grade__isnull=True
    ).select_related("assignment", "student").order_by("submitted_at")

    # Fix: use values_list to ensure a list of IDs
    students_count = User.objects.filter(
    enrollments_user__course__in=my_courses.values_list('id', flat=True)
      ).distinct().count()


    return {
        "upcoming_classes": upcoming_classes,
        "assignments_to_grade": assignments_to_grade,
        "students_count": students_count,
        "courses_count": my_courses.count(),
        "my_courses": my_courses
    }



# ===================== Admin Dashboard =====================
def admin_dashboard(limit=5):
    now = timezone.now()
    upcoming_classes = (
        ClassSession.objects.filter(start_time__gte=now)
        .select_related("course")
        .order_by("start_time")[:limit]
    )

    # Admin sees all announcements
    announcements = Announcement.objects.order_by("-created_at")[:limit]

    counts = User.objects.values("role").annotate(c=Count("id"))
    role_counts = {item["role"]: item["c"] for item in counts}

    return {
        "upcoming_classes": upcoming_classes,
        "announcements": announcements,
        "stats": {
            "users_admin": role_counts.get("ADMIN", 0),
            "users_teacher": role_counts.get("TEACHER", 0),
            "users_student": role_counts.get("STUDENT", 0),
            "courses_count": Course.objects.count(),
            "assignments_count": Assignment.objects.count(),
        },
    }
