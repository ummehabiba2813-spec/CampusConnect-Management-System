from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
from django.contrib import admin
from .models import TeacherProfile 

admin.site.register(TeacherProfile)
class CustomUserAdmin(BaseUserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
        "email_verified",
    )
    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        "role",
        "email_verified",
    )

# ✅ yahan sirf ek hi registration rakho
admin.site.register(User, CustomUserAdmin)
