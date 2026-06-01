from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django import forms
from django.core.exceptions import PermissionDenied
import datetime

# --- Models and Forms Imports ---
from accounts.models import User, TeacherProfile
from accounts.decorators import role_required
from academics.models import (
    Assignment, Course, Enrollment, LectureMaterial, 
    Submission, Department, Announcement, Material, Timetable
)
from .forms import (
    AssignmentUploadForm, AssignmentManualForm, CourseForm,
    LectureMaterialForm, AssignmentForm, SubmissionForm,
    AnnouncementForm, MaterialForm, TimetableForm
)

# ===================== Course Views =====================

@method_decorator(login_required, name="dispatch")
class CourseListView(ListView):
    model = Course
    template_name = "courses/course_list.html"
    paginate_by = 20
    def get_queryset(self):
        qs = Course.objects.select_related("department", "teacher")
        q = self.request.GET.get("q")
        return qs.filter(title__icontains=q) if q else qs

@method_decorator(login_required, name="dispatch")
class CourseDetailView(DetailView):
    model = Course
    template_name = "courses/course_detail.html"

@method_decorator([login_required, role_required("ADMIN")], name="dispatch")
class CourseCreateView(CreateView):
    model = Course; form_class = CourseForm; template_name = "courses/course_form.html"
    def get_success_url(self): return reverse("course-detail", args=[self.object.pk])

@method_decorator([login_required, role_required("ADMIN")], name="dispatch")
class CourseUpdateView(UpdateView):
    model = Course; form_class = CourseForm; template_name = "courses/course_form.html"
    def get_success_url(self): return reverse("course-detail", args=[self.object.pk])

@method_decorator([login_required, role_required("ADMIN")], name="dispatch")
class CourseDeleteView(DeleteView):
    model = Course; template_name = "courses/confirm_delete.html"
    def get_success_url(self): return reverse("course-list")

# ===================== Teacher Functions =====================

@login_required
@role_required("TEACHER")
def upload_material(request, pk):
    course = get_object_or_404(Course, pk=pk, teacher=request.user)
    if request.method == "POST":
        form = LectureMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.course = course
            obj.uploaded_by = request.user
            obj.save()
            messages.success(request, "Material uploaded.")
            return redirect("course-detail", pk=pk)
    else:
        form = LectureMaterialForm()
    return render(request, "academics/material_form.html", {"form": form, "course": course})

@login_required
@role_required("TEACHER")
def manage_assignments(request):
    assignments = Assignment.objects.filter(created_by=request.user).order_by("-created_at")
    assignments_by_class = {}
    for asg in assignments:
        class_name = asg.class_name if asg.class_name else "Unassigned Class"
        if class_name not in assignments_by_class:
            assignments_by_class[class_name] = []
        assignments_by_class[class_name].append(asg)
    return render(request, "assignments/manage_assignments.html", {"assignments_by_class": assignments_by_class})

@login_required
def delete_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    if request.method == "POST":
        assignment.delete()
        messages.success(request, "Assignment deleted successfully.")
        return redirect("manage_assignments")
    return render(request, "assignments/delete_assignment_confirm.html", {"assignment": assignment})

# ===================== Student & Enrollment =====================

@login_required
@role_required("STUDENT")
def enroll_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    Enrollment.objects.get_or_create(course=course, student=request.user)
    messages.success(request, f"Enrolled in {course.title}.")
    return redirect("course-detail", pk=pk)

@login_required
@role_required("STUDENT")
def unenroll_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    Enrollment.objects.filter(course=course, student=request.user).delete()
    messages.info(request, f"Un-enrolled from {course.title}.")
    return redirect("course-detail", pk=pk)

# ===================== Timetable & Dashboard =====================
from .models import Timetable, Day
# academics/views.py
@login_required
@role_required("ADMIN")
def manage_timetable(request):
    # Purana sara data dikhane ke liye
    schedules = Timetable.objects.all().order_by('day__id', 'start_time') 
    
    if request.method == "POST":
        form = TimetableForm(request.POST)
        # Checkboxes se selected dinon ki list
        selected_day_ids = request.POST.getlist('selected_days') 
        
        if form.is_valid() and selected_day_ids:
            # Common data uthana
            course = form.cleaned_data['course']
            teacher = form.cleaned_data['teacher']
            room = form.cleaned_data['room_number']
            credits = form.cleaned_data['credit_hours']
            
            for day_id in selected_day_ids:
                # Har selected day ke liye uska apna time slot uthana
                start = request.POST.get(f'start_time_{day_id}')
                end = request.POST.get(f'end_time_{day_id}')
                
                if start and end:
                    # Naya record database mein save karna
                    Timetable.objects.create(
                        course=course,
                        teacher=teacher,
                        day_id=day_id,
                        start_time=start,
                        end_time=end,
                        room_number=room,
                        credit_hours=credits
                    )
            
            messages.success(request, "Naya schedule save ho gaya!")
            return redirect('manage_timetable')
    else:
        form = TimetableForm()
    
    return render(request, "admin/manage_timetable.html", {
        "form": form, 
        "schedules": schedules,
        "days": Day.objects.all().order_by('id') # Template ko days ki list dena
    })
# ===================== Missing Functions (Added) =====================

@login_required
@role_required("STUDENT")
def create_submission(request, assignment_pk):
    assignment = get_object_or_404(Assignment, pk=assignment_pk)
    if request.method == "POST":
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.assignment = assignment
            submission.student = request.user
            submission.save()
            messages.success(request, "Assignment submitted successfully!")
            return redirect("course-detail", pk=assignment.course.pk)
    else:
        form = SubmissionForm()
    return render(request, "assignments/submission_form.html", {"form": form, "assignment": assignment})

@login_required
@role_required("TEACHER")
def grade_submission(request, submission_pk=None):
    # 1. Agar specific submission ko grade karna hai
    if submission_pk:
        submission = get_object_or_404(Submission, pk=submission_pk)
        
        if request.method == "POST":
            grade = request.POST.get('grade')
            feedback = request.POST.get('feedback')
            
            submission.grade = grade
            submission.feedback = feedback
            submission.save()
            
            messages.success(request, f"Grades updated for {submission.student.username}")
            return redirect('assignment_submissions', assignment_id=submission.assignment.id)
        
        # Yeh return 'if submission_pk' ke andar hona chahiye
        return render(request, "assignments/grade_submission.html", {"submission": submission})

    return render(request, "assignments/assignment_submissions.html")
@login_required
def delete_assignment_confirm(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    return render(request, 'assignments/delete_assignment_confirm.html', {'assignment': assignment})

@login_required
@role_required("TEACHER")
def edit_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    if request.method == "POST":
        form = AssignmentForm(request.POST, request.FILES, instance=assignment)
        if form.is_valid():
            form.save()
            messages.success(request, "Assignment updated!")
            return redirect("manage_assignments")
    else:
        form = AssignmentForm(instance=assignment)
    return render(request, "assignments/assignment_form.html", {"form": form})

@login_required
def assignment_submissions(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    submissions = Submission.objects.filter(assignment=assignment)
    return render(request, 'assignments/assignment_submissions.html', {'assignment': assignment, 'submissions': submissions})

@login_required
@role_required("STUDENT")
def submit_assignment_view(request, assignment_id):
    # Ye apka redundant path ho sakta hai, create_submission jaisa hi kaam karega
    return redirect('submission-create', assignment_pk=assignment_id)

@login_required
def student_courses(request):
    enrollments = Enrollment.objects.filter(student=request.user)
    return render(request, 'courses/student_courses.html', {'enrollments': enrollments})

@login_required
@role_required("ADMIN")
def manage_courses(request):
    courses = Course.objects.all()
    return render(request, "courses/manage_courses.html", {"courses": courses})

@login_required
@role_required("ADMIN")
def add_course(request):
    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("manage_courses")
    else:
        form = CourseForm()
    return render(request, "courses/course_form.html", {"form": form})

@login_required
@role_required("ADMIN")
def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == "POST":
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect("manage_courses")
    else:
        form = CourseForm(instance=course)
    return render(request, "courses/course_form.html", {"form": form})

@login_required
@role_required("ADMIN")
def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == "POST":
        course.delete()
        return redirect("manage_courses")
    return render(request, "courses/confirm_delete.html", {"course": course})

@login_required
def edit_department(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    # Edit logic
    return render(request, "departments/add_department.html", {"dept": dept})

@login_required
def delete_department(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    dept.delete()
    return redirect("manage_departments")
# academics/views.py

@login_required
@role_required("TEACHER")
def teacher_dashboard(request):
    try:
        # Teacher profile fetch karein
        teacher_profile = request.user.teacher_profile
    except (AttributeError, TeacherProfile.DoesNotExist):
        return render(request, "dashboard/error.html", {"message": "Profile Missing!"})

    # Aaj ka din (e.g., 'Monday')
    today_full = datetime.datetime.now().strftime('%A')
    
    
    todays_schedule = Timetable.objects.filter(
        teacher=teacher_profile, 
        days__name=today_full
    ).distinct().order_by('start_time')

    # Courses jo is teacher ke profile ID se linked hain
    courses = Course.objects.filter(teacher_id=teacher_profile.id)
    
    # Assignments jo is teacher ki class ke liye hain
    assignments = Assignment.objects.filter(class_name=teacher_profile.class_name).order_by('-created_at')

    context = {
        'schedule': todays_schedule,
        'courses': courses,
        'assignments': assignments,
        'total_courses': courses.count(),
        'today_name': today_full,
    }
    return render(request, 'dashboard/teacher_dashboard.html', context)

@login_required
@role_required("TEACHER")
def teacher_courses(request):
    try:
        # Teacher profile dhoondna
        teacher_profile = request.user.teacher_profile
        # Error Fix: 'teacher__user' ya 'teacher' ki jagah 'teacher_id' use karein
        courses = Course.objects.filter(teacher_id=teacher_profile.id)
    except (AttributeError, TeacherProfile.DoesNotExist):
        courses = []
        messages.error(request, "Teacher profile not found.")
        
    return render(request, 'dashboard/teacher_courses.html', {'courses': courses})


# ===================== Department Management =====================

@login_required
def manage_departments(request):
    departments = Department.objects.all()
    return render(request, "departments/manage_departments.html", {"departments": departments})
@login_required
@role_required("TEACHER")
def create_assignment(request):
    if request.method == "POST":
        form = AssignmentForm(request.POST, request.FILES)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.created_by = request.user
            assignment.save()
            messages.success(request, "Assignment created successfully!")
            return redirect("manage_assignments")
    else:
        form = AssignmentForm()
    return render(request, "assignments/create_assignment.html", {"form": form})
@login_required
def add_department(request):
    if request.method == "POST":
        code = request.POST.get("code")
        name = request.POST.get("name")
        Department.objects.create(code=code, name=name)
        return redirect("manage_departments")
    return render(request, "departments/add_department.html")