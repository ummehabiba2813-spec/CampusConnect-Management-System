from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = "admin", "Admin"
        TEACHER = "teacher", "Teacher"
        STUDENT = "student", "Student"

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.STUDENT
    )
    email_verified = models.BooleanField(default=False)

    # Teacher-specific fields
    assigned_class = models.CharField(max_length=100, blank=True, null=True)
    qualifications = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_photo = models.ImageField(upload_to="teachers/", blank=True, null=True)

    def is_admin(self):
        return self.role == self.Roles.ADMIN

    def is_teacher(self):
        return self.role == self.Roles.TEACHER

    def is_student(self):
        return self.role == self.Roles.STUDENT


class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="teacher_profile")
    qualification = models.CharField(max_length=255)
    class_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.user.username} - {self.qualification}"



from django.db import models

class Teacher(models.Model):
    teacher_id = models.CharField(
        max_length=50,
        unique=True,
        blank=True,  # abhi empty chhod sakte hain
        null=True
    )

    name = models.CharField(max_length=100)
    qualification = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    class_name = models.CharField(max_length=50)
    experience_years = models.PositiveIntegerField()
    section = models.CharField(max_length=10)
    session = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.teacher_id or 'TBD'} - {self.name}"



class Student(models.Model):
    name = models.CharField(max_length=100)
    father_name = models.CharField(max_length=100)
    cnic = models.CharField(max_length=15, unique=True)   # ✅ CNIC unique
    roll_no = models.CharField(max_length=20, unique=True)  # ✅ Roll no unique
    class_name = models.CharField(max_length=50)
    class_section = models.CharField(max_length=10, blank=True, null=True)
    dob = models.DateField()
    address = models.TextField()
    department = models.ForeignKey("academics.Department", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.roll_no})"
    from django.db import models
# -----------------------admin profile---------------------
class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to="admin_profiles/", blank=True, null=True)
    full_name = models.CharField(max_length=200)
    cnic = models.CharField(max_length=20, unique=True)
    qualification = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.full_name
