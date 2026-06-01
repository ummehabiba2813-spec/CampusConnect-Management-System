from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

User = get_user_model()

# ---------------- Attendance Views ----------------
@login_required
def mark_attendance(request, course_id):
    return HttpResponse(f"Mark attendance for course {course_id}")

@login_required
def attendance_list(request, course_id):
    return HttpResponse(f"Attendance list for course {course_id}")

# ---------------- Inbox / Messaging ----------------
@login_required
def inbox(request):
    # Replace with actual messages query
    messages = []
    return render(request, "campusconnect/inbox.html", {"messages": messages})

@login_required
def send_message(request, user_id):
    recipient = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        content = request.POST.get("content")
        # Replace with your Message model logic
        # Example: Message.objects.create(sender=request.user, recipient=recipient, content=content)
        return redirect("inbox")

    return render(request, "campusconnect/send_message.html", {"recipient": recipient})

# ---------------- Course Search ----------------
# ---------------- Course Search ----------------
@login_required
def search(request):
    from academics.models import Course
    from django.db.models import Q

    query = request.GET.get("q", "")
    results = []
    
    if query:
        results = Course.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    
    # Ye niche wali line 'if' ke barabar nahi, balke 'query' ke barabar honi chahiye
    return render(request, "campusconnect/search.html", {"results": results, "query": query})
# ---------------- Assignments Filter ----------------
@login_required
def filter_assignments(request):
    from academics.models import Assignment
    assignments = Assignment.objects.all()
    # Example: filter by course_id from GET parameter
    course_id = request.GET.get("course_id")
    if course_id:
        assignments = assignments.filter(course_id=course_id)
    return render(request, "campusconnect/assignments.html", {"assignments": assignments})
from django.shortcuts import render

def announcement_list(request):
    # Replace with actual query
    announcements = []
    return render(request, "announcements/list.html", {"announcements": announcements})
