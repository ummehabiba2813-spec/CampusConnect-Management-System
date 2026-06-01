from django import forms
from .models import Course, LectureMaterial, Assignment, Submission, Announcement, Material, Department
from accounts.models import User
from .models import Timetable

# ---------- LectureMaterial Form ----------
class LectureMaterialForm(forms.ModelForm):
    class Meta:
        model = LectureMaterial
        fields = ["title","file","file_type"]


# ---------- Assignment Form ----------
from django import forms
from .models import Assignment


class AssignmentForm(forms.ModelForm):
    due_at = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"})
    )

    class Meta:
        model = Assignment
        fields = ["title", "description", "due_at", "total_marks", "class_name", "section"]
        # 'course' hata diya

from django import forms
from .models import Assignment

class AssignmentUploadForm(forms.ModelForm):
    due_at = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"})
    )

    class Meta:
        model = Assignment
        fields = ["title", "description", "due_at", "file", "total_marks", "questions", "class_name", "section"]


class AssignmentManualForm(forms.ModelForm):
    due_at = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"})
    )

    class Meta:
        model = Assignment
        fields = ["title", "description", "due_at", "total_marks", "class_name", "section", "questions"]
        widgets = {
            "questions": forms.Textarea(attrs={"rows": 3, "cols": 50, "maxlength": 5000}),
        }


# ---------- Submission Form ----------
class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ["file"]


# ---------- Course Form ----------
# academics/forms.py
from django import forms
from .models import Course, Department


class CourseForm(forms.ModelForm):
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'maxlength': '500',
        })
    )

    class Meta:
        model = Course
        fields = [
            'code',
            'title',
            'description',
            'teacher_name',
            'teacher_id',
            'department',
            'class_name',
            'section',
        ]

        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),

            'teacher_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Teacher Name'
            }),

            'teacher_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Unique Teacher ID'
            }),

            'class_name': forms.TextInput(attrs={'class': 'form-control'}),
            'section': forms.TextInput(attrs={'class': 'form-control'}),
        }

# ---------- Announcement Form ----------
class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'body', 'created_by']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'maxlength': 1000}),
            'created_by': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your name'}),
        }


# ---------- Material Form ----------
class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['title', 'file']



# academics/forms.py
from django import forms
from .models import Timetable, Day

class TimetableForm(forms.ModelForm):
    class Meta:
        model = Timetable
        fields = ['course', 'teacher', 'room_number', 'credit_hours'] 
        widgets = {
            'teacher': forms.Select(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'room_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Lab 01'}),
            'credit_hours': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.all_days = Day.objects.all().order_by('id')