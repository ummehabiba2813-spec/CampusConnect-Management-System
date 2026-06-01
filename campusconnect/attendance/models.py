# attendance/models.py
from django.db import models
from accounts.models import Teacher, User  # Teacher ko import kiya

from accounts.models import TeacherProfile, User  

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class AttendanceSheet(models.Model):
    class_name = models.CharField(max_length=100)
    section = models.CharField(max_length=50)
    session = models.CharField(max_length=100, default="2025")  
    teacher = models.ForeignKey("accounts.Teacher", on_delete=models.CASCADE)  # simple relation
    course_code = models.CharField(max_length=50)
    course_name = models.CharField(max_length=100)
    month = models.CharField(max_length=20)
    created_by = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="created_sheets")
    created_at = models.DateTimeField(auto_now_add=True)



class AttendanceRecord(models.Model):
    sheet = models.ForeignKey(AttendanceSheet, on_delete=models.CASCADE, related_name="records")
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role__iexact': 'STUDENT'})
    total_classes = models.IntegerField(default=0)
    attended_classes = models.IntegerField(default=0)

    @property
    def percentage(self):
        if self.total_classes == 0:
            return 0
        return round((self.attended_classes / self.total_classes) * 100, 2)

    def __str__(self):
        return f"{self.student.username} - {self.sheet}"
