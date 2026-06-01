from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Announcement
from .forms import AnnouncementForm
from django.shortcuts import get_object_or_404, redirect, render

def teacher_or_admin(user):
    return user.is_authenticated and user.role in ["admin", "teacher"]

# ----------------------------
# Manage Announcements (ALL ROLES)
# ----------------------------
@login_required
def manage_announcements(request):
    announcements = Announcement.objects.all()
    # Case-insensitive check for role
    can_manage = request.user.role.upper() in ["ADMIN", "TEACHER"]
    return render(
        request,
        "announcements/manage_announcements.html",
        {"announcements": announcements, "can_manage": can_manage},
    )


# ----------------------------
# Add Announcement (ADMIN + TEACHER only)
# ----------------------------

@login_required
def add_announcement(request):
    if request.user.role.upper() not in ["ADMIN", "TEACHER"]:
        return redirect("announcements:manage_announcements")  # students cannot add

    if request.method == "POST":
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.created_by = request.user
            announcement.save()
            return redirect("announcements:manage_announcements")
    else:
        form = AnnouncementForm()

    return render(request, "announcements/add_announcement.html", {"form": form})


# ----------------------------
# Edit Announcement (ADMIN + TEACHER only)
# ----------------------------
@login_required
def edit_announcement(request, announcement_id):
    if request.user.role.upper() not in ["ADMIN", "TEACHER"]:
        return redirect("announcements:manage_announcements")

    announcement = get_object_or_404(Announcement, id=announcement_id)
    if request.method == "POST":
        form = AnnouncementForm(request.POST, instance=announcement)
        if form.is_valid():
            form.save()
            return redirect("announcements:manage_announcements")
    else:
        form = AnnouncementForm(instance=announcement)
    return render(request, "announcements/edit_announcement.html", {"form": form})


# ----------------------------
# Delete Announcement (ADMIN + TEACHER only)
# ----------------------------
@login_required
def delete_announcement(request, announcement_id):
    if request.user.role.upper() not in ["ADMIN", "TEACHER"]:
        return redirect("announcements:manage_announcements")

    announcement = get_object_or_404(Announcement, id=announcement_id)
    if request.method == "POST":
        announcement.delete()
        return redirect("announcements:manage_announcements")
    return render(request, "announcements/delete_announcement.html", {"announcement": announcement})
