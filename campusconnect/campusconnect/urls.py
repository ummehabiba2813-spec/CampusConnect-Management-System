from django.contrib import admin
from django.urls import path, include
from accounts.views import DashboardView
from . import views
from django.conf import settings
from django.conf.urls.static import static
from academics import views as course_views   # ✅ change here

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("announcements/", include(("announcements.urls", "announcements"), namespace="announcements")),
    path("api/", include("api.urls")),
    path("academics/", include("academics.urls")),   # ✅ keep only this

    # Default route → dashboard
    path("", DashboardView.as_view(), name="dashboard"),

    # Attendance & messaging
    path("<int:course_id>/mark/", views.mark_attendance, name="mark_attendance"),
    path("<int:course_id>/", views.attendance_list, name="attendance_list"),
    path("inbox/", views.inbox, name="inbox"),
    path("send/<int:user_id>/", views.send_message, name="send_message"),
    path("search/", views.search, name="course_search"),
    path("assignments/filter/", views.filter_assignments, name="filter_assignments"),

    # ✅ enrolled courses view from academics instead of courses
    path("academics/enroll/", course_views.enroll_course, name="enroll_course"),

    path("attendance/", include("attendance.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
