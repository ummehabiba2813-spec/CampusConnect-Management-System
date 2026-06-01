from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Auth
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("login/", auth_views.LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    # Universal Dashboard (auto-redirects based on role)
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),

    # Role-specific dashboards
path("admin/dashboard/", views.admin_dashboard, name="admin_dashboard"),
path("teacher-dashboard/", views.teacher_dashboard, name="teacher_dashboard"),
    path("student-dashboard/", views.student_dashboard, name="student_dashboard"),

    path("create-profile/", views.create_admin_profile, name="create_admin_profile"),

    # Email verification
    path("verify-email/<uidb64>/<token>/", views.verify_email, name="verify-email"),
    path("resend-verification/", views.ResendVerificationView.as_view(), name="resend-verification"),

    # Password reset
    path("password-reset/", auth_views.PasswordResetView.as_view(), name="password_reset"),
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),

    # Admin: Add Users
    path("teachers/", views.teacher_list, name="teacher_list"),
    path("teachers/add/", views.add_teacher, name="add_teacher"),
    path("teachers/edit/<int:id>/", views.edit_teacher, name="edit_teacher"),
    path("teachers/delete/<int:id>/", views.delete_teacher, name="delete_teacher"),

    path("students/", views.student_list, name="student_list"),
    path("students/add/", views.add_student, name="add_student"),
    path("students/edit/<int:pk>/", views.edit_student, name="edit_student"),
    path("students/<int:pk>/delete/", views.delete_student, name="delete_student"),
]
