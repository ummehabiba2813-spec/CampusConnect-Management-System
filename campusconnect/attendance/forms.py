# attendance/forms.py

from django import forms
from .models import AttendanceSheet
from accounts.models import Teacher
from django.contrib.contenttypes.models import ContentType


class AttendanceSheetForm(forms.ModelForm):
    teacher = forms.ModelChoiceField(
        queryset=Teacher.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"})
    )

    class Meta:
        model = AttendanceSheet
        fields = ["class_name", "section", "session", "teacher", "course_code", "course_name", "month"]
        widgets = {
            "class_name": forms.TextInput(attrs={"class": "form-control"}),
            "section": forms.TextInput(attrs={"class": "form-control"}),
            "session": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Session"}),
            "course_code": forms.TextInput(attrs={"class": "form-control"}),
            "course_name": forms.TextInput(attrs={"class": "form-control"}),
            "month": forms.TextInput(attrs={"class": "form-control"}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)

        # set teacher as GenericForeignKey
        teacher = self.cleaned_data["teacher"]
        instance.teacher_content_type = ContentType.objects.get_for_model(teacher)
        instance.teacher_object_id = teacher.id

        if commit:
            instance.save()
        return instance
