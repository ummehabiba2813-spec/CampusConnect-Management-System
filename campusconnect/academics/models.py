from django.conf import settings
from django.db import models
from django.utils import timezone

User = settings.AUTH_USER_MODEL


# ---------------- Department ----------------
class Department(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# ---------------- Course ----------------
class Course(models.Model):
    code = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # ✅ KEEP teacher_id (used elsewhere)
    teacher_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Unique Teacher ID"
    )

    # ✅ readable teacher name
    teacher_name = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    class_name = models.CharField(max_length=50, blank=True, null=True)
    section = models.CharField(max_length=10, blank=True, null=True)

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="courses"
    )

    def __str__(self):
        return f"{self.code} - {self.title}"


# ---------------- Enrollment ----------------
class Enrollment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="enrollments")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("course", "student")


# ---------------- ClassSession ----------------
class ClassSession(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="sessions")
    topic = models.CharField(max_length=200)
    start_time = models.DateTimeField(db_index=True)
    end_time = models.DateTimeField()
    room = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ["start_time"]

    def is_upcoming(self):
        return self.start_time >= timezone.now()


# ---------------- Attendance ----------------
class Attendance(models.Model):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"

    STATUS_CHOICES = [
        (PRESENT, "Present"),
        (ABSENT, "Absent"),
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="attendance")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="attendance")
    session = models.ForeignKey(ClassSession, on_delete=models.CASCADE, related_name="attendance")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=ABSENT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "session")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student} - {self.course.code} - {self.status}"

    def is_present(self):
        return self.status == self.PRESENT


# ---------------- Announcement ----------------
class Announcement(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    created_by = models.CharField(max_length=150, default="System")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


# ---------------- LectureMaterial ----------------
def material_upload_path(instance, filename):
    return f"materials/course_{instance.course_id}/{filename}"


class LectureMaterial(models.Model):
    PDF, PPT, VIDEO, OTHER = "PDF", "PPT", "VIDEO", "OTHER"

    TYPES = [
        (PDF, "PDF"),
        (PPT, "PPT"),
        (VIDEO, "Video"),
        (OTHER, "Other"),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="materials")
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to=material_upload_path)
    file_type = models.CharField(max_length=10, choices=TYPES, default=OTHER)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# ---------------- Assignment ----------------
class Assignment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_at = models.DateTimeField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to="assignments/", blank=True, null=True)
    total_marks = models.PositiveIntegerField(null=True, blank=True)
    questions = models.TextField(blank=True)

    class_name = models.CharField(max_length=50, blank=True)
    section = models.CharField(max_length=50, blank=True)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assignments")

    def __str__(self):
        return self.title


# ---------------- Submission ----------------
def submission_upload_path(instance, filename):
    return f"submissions/assignment_{instance.assignment_id}/user_{instance.student_id}/{filename}"


class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="submissions")
    file = models.FileField(upload_to=submission_upload_path, blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True)

    class Meta:
        unique_together = ("assignment", "student")


# ---------------- Simple Material ----------------
class Material(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="simple_materials")
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to="materials/")
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# ---------------- Timetable ----------------
# academics/models.py

class Day(models.Model):
    name = models.CharField(max_length=10, unique=True) # Monday, Tuesday...
    code = models.CharField(max_length=3, unique=True)   # MON, TUE...

    def __str__(self):
        return self.name

# academics/models.py
class Timetable(models.Model):
    course = models.ForeignKey("academics.Course", on_delete=models.CASCADE, related_name="timetables")
    teacher = models.ForeignKey("accounts.TeacherProfile", on_delete=models.CASCADE, related_name="timetables")
    
    # Aik entry aik hi din aur aik hi time ki hogi
    day = models.ForeignKey(Day, on_delete=models.CASCADE, related_name="timetables")
    
    start_time = models.TimeField()
    end_time = models.TimeField()
    room_number = models.CharField(max_length=50)
    credit_hours = models.PositiveIntegerField(default=3)

    def __str__(self):
        return f"{self.course.title} | {self.day.name} | {self.start_time}"