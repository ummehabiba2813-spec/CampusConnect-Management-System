from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
import re
from django import forms
from .models import Teacher
from .models import Student
from .models import AdminProfile

User = get_user_model()  # Custom user ko load karega
class CampusSignUpForm(UserCreationForm):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    ]

    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True, label="Role")

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'password1', 'password2']
        labels = {
            'username': 'Campus ID',
            'email': 'Email Address',
            'password1': 'Password',
            'password2': 'Confirm Password',
        }

    # ✅ Username Validation
    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Allow letters, numbers, and @ . + - _
        if not re.match(r'^[A-Za-z0-9@.+\-_]+$', username):
            raise forms.ValidationError(
                "Campus ID may contain letters, numbers, and @/./+/-/_ only."
            )
        return username


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username or Email")
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")



class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['name', 'qualification', 'subject','teacher_id', 'class_name', 'section', 'session', 'experience_years']
        widgets = {
           'teacher_id': forms.TextInput(attrs={'placeholder': 'Unique ID e.g. TCHR-001!'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'class_name': forms.TextInput(attrs={'class': 'form-control'}),
            'section': forms.TextInput(attrs={'class': 'form-control'}),
            'session': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 2025-2026 or Special123!'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }


    def clean_session(self):
        session = self.cleaned_data.get('session')
        if not session:
            raise forms.ValidationError("Session is required.")
        if not re.match(r'^[\w\-!@#$%^&*() ]+$', session):
            raise forms.ValidationError("Session can only contain letters, numbers, and special characters.")
        return session

    def clean_teacher_id(self):
        teacher_id = self.cleaned_data.get("teacher_id")
        if Teacher.objects.filter(teacher_id__iexact=teacher_id).exists():
            raise forms.ValidationError("This Teacher ID already exists. Please choose a different ID.")
        return teacher_id
from .models import Student

from django import forms
from .models import Student

# accounts/forms.py
from django import forms
from .models import Student
import re



class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            "name",
            "father_name",
            "cnic",
            "roll_no",
            "class_name",
            "class_section",
            "dob",
            "address",
            "department",
           
        ]

        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter full name"}),
            "father_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter father's name"}),
            "cnic": forms.TextInput(attrs={"class": "form-control", "placeholder": "12345-1234567-1"}),
            "roll_no": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter roll number"}),
            "class_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter class"}),
            "class_section": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter section"}),
            "dob": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Enter address"}),
            "department": forms.Select(attrs={"class": "form-control"}),
        }

    # ✅ CNIC format + uniqueness check
    def clean_cnic(self):
        cnic = self.cleaned_data.get("cnic")
        pattern = r"^\d{5}-\d{7}-\d{1}$"

        if not re.match(pattern, cnic):
            raise forms.ValidationError("❌ Enter CNIC in correct format (12345-1234567-1).")

        qs = Student.objects.filter(cnic=cnic)
        # 👉 Edit ke waqt current student ko ignore karo
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError("❌ This CNIC is already registered.")

        return cnic

    # ✅ Roll No uniqueness check
    def clean_roll_no(self):
        roll_no = self.cleaned_data.get("roll_no")
        qs = Student.objects.filter(roll_no=roll_no)
        # 👉 Edit ke waqt current student ko ignore karo
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError("❌ This roll number is already assigned. Choose another.")

        return roll_no

      # ✅ admin profile form

from django import forms
from .models import AdminProfile

class AdminProfileForm(forms.ModelForm):
    class Meta:
        model = AdminProfile
        fields = ['profile_picture', 'full_name', 'cnic', 'qualification', 'phone', 'address']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'cnic': forms.TextInput(attrs={'class': 'form-control'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


