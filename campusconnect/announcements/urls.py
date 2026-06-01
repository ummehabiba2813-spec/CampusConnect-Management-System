from django.urls import path
from . import views

app_name = "announcements"

urlpatterns = [
    path("", views.manage_announcements, name="manage_announcements"),
    path("add/", views.add_announcement, name="add_announcement"),
    path("edit/<int:announcement_id>/", views.edit_announcement, name="edit_announcement"),
    path("delete/<int:announcement_id>/", views.delete_announcement, name="delete_announcement"),
]

