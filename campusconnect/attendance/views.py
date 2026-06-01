# attendance/views.py
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from academics.models import Attendance, Course, ClassSession  # from academics
from .models import AttendanceSheet, AttendanceRecord          # from attendance app
from accounts.models import User, Teacher
from accounts.decorators import role_required
from .forms import AttendanceSheetForm

# ----------------------------
# Create Attendance Sheet (ADMIN only)
# ----------------------------
# attendance/views.py


@login_required
def create_attendance_sheet(request):
    if request.user.role.upper() != "ADMIN":
        return redirect("manage_attendance")

    if request.method == "POST":
        form = AttendanceSheetForm(request.POST)
        if form.is_valid():
            sheet = form.save(commit=False)
            sheet.created_by = request.user
            sheet.save()
            messages.success(request, "Attendance sheet created successfully.")
            return redirect("manage_attendance")
    else:
        form = AttendanceSheetForm()

    return render(request, "attendance/attendance_form.html", {"form": form})


# ----------------------------
# Mark Attendance (ADMIN + TEACHER)
# ----------------------------

@login_required
@role_required("TEACHER")
def mark_attendance(request, sheet_id):
    sheet = get_object_or_404(AttendanceSheet, id=sheet_id)
    
    # prevent editing finalized sheet
    if sheet.is_finalized:
        messages.error(request, "Attendance already finalized.")
        return redirect("manage_attendance")
    
    students = User.objects.filter(role="STUDENT", attendance__session__course__code=sheet.course_code).distinct()
    
    if request.method == "POST":
        for student in students:
            total = int(request.POST.get(f"total_{student.id}", 0))
            attended = int(request.POST.get(f"attended_{student.id}", 0))
            
            record, _ = AttendanceRecord.objects.get_or_create(sheet=sheet, student=student)
            record.total_classes = total
            record.attended_classes = attended
            record.save()
        
        sheet.is_finalized = True
        sheet.save()
        messages.success(request, "Attendance saved successfully.")
        return redirect("manage_attendance")

    records = {rec.student.id: rec for rec in AttendanceRecord.objects.filter(sheet=sheet)}
    return render(request, "attendance/mark_attendance.html", {"sheet": sheet, "students": students, "records": records})

# ----------------------------
# Manage Attendance (ADMIN + TEACHER)
# ----------------------------
@login_required
def manage_attendance(request):
    sheets = AttendanceSheet.objects.all().order_by("-created_at")  # sab sheets latest first

    context = {
        "sheets": sheets,
        "is_admin": request.user.role.lower() == "admin",
        "is_teacher": request.user.role.lower() == "teacher",
    }
    return render(request, "attendance/manage_attendance.html", context)


# ----------------------------
# Attendance List (STUDENT only)
# ----------------------------
def attendance_list(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    attendances = Attendance.objects.filter(course=course)

    context = {
        "course": course,
        "attendances": attendances,
    }
    return render(request, "academics/attendance_list.html", context)

# ----------------------------
# View Attendance (ALL ROLES)
# ----------------------------
@login_required
@role_required("STUDENT")
def view_attendance(request):
    student = request.user
    attendance = Attendance.objects.filter(student=student)

    if not attendance.exists():
        message = "No attendance uploaded yet."
        return render(request, "attendance/view_attendance.html", {"message": message})

    return render(request, "attendance/view_attendance.html", {"attendance": attendance})



@login_required
def get_teachers(request):
    session = request.GET.get("session")
    teachers = Teacher.objects.filter(session=session).values("id", "name", "teacher_id")
    return JsonResponse(list(teachers), safe=False)

# attendance/views.py


@login_required
def get_teachers_by_session(request):
    session = request.GET.get("session")
    teachers = Teacher.objects.filter(session=session).values("id", "name", "teacher_id").order_by("name")
    return JsonResponse(list(teachers), safe=False)




@login_required
@role_required("STUDENT")
def student_attendance(request):
    student = request.user
    sheets = AttendanceSheet.objects.filter(records__student=student).distinct()
    attendance_data = {sheet: sheet.records.filter(student=student) for sheet in sheets}

    if not sheets.exists():
        message = "No attendance uploaded yet."
        return render(request, "attendance/student_attendance.html", {"message": message})

    return render(request, "attendance/student_attendance.html", {"attendance_data": attendance_data})



@login_required
def get_students(request):
    class_name = request.GET.get("class_name")
    section = request.GET.get("section")
    session = request.GET.get("session")

    students = User.objects.filter(
        role="STUDENT",
        student_profile__class_name__iexact=class_name,
        student_profile__section__iexact=section,
        student_profile__session__iexact=session
    ).values("id", "username", "first_name", "last_name")

    return JsonResponse(list(students), safe=False)
