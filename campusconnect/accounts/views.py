from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.shortcuts import redirect, render, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import CreateView, TemplateView, FormView
from django.conf import settings
from academics.models import Course
from announcements.models import Announcement
# ===================== Local imports =====================
from .forms import (
    TeacherForm,
    StudentForm,
    CampusSignUpForm,
    AdminProfileForm,
)
from .models import User, Teacher, Student, AdminProfile
from .tokens import email_verification_token

# Agar aapko sirf apni local dashboards chahiye to ye import hata dein:
# from academics.services import student_dashboard, teacher_dashboard, admin_dashboard


# ===================== Dashboard =====================
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/dashboard.html"
    login_url = "login"

    def dispatch(self, request, *args, **kwargs):
        u = request.user
        
        # 1. Login check
        if not u.is_authenticated:
            return redirect("login")

        # 2. Admin Logic
        if u.role == "admin":
            try:
                # Check if profile exists
                _ = u.adminprofile
            except AdminProfile.DoesNotExist:
                # Agar profile nahi hai to create profile par bhejein
                request.session["redirect_after_profile"] = reverse("admin_dashboard")
                return redirect("create_admin_profile")
            
            # AGAR profile hai, to naye admin_dashboard par bhejein
            return redirect("admin_dashboard")

        # 3. Teacher Logic
        elif u.role == "teacher":
            return redirect("teacher_dashboard")

        # 4. Student Logic
        elif u.role == "student":
            return redirect("student_dashboard")

        # Default fallback agar koi role match na kare
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        u = self.request.user
        ctx["greeting"] = f"Welcome, {u.get_full_name() or u.username}"
        ctx["role"] = getattr(u, "role", None)
        return ctx

# ===================== Create Admin Profile =====================
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .forms import AdminProfileForm
from .models import AdminProfile

@login_required
def create_admin_profile(request):
    # Check if profile already exists
    profile = getattr(request.user, "adminprofile", None)

    if profile:  
        return redirect("admin_dashboard")

    if request.method == "POST":
        form = AdminProfileForm(request.POST, request.FILES)
        if form.is_valid():
            admin_profile = form.save(commit=False)
            admin_profile.user = request.user
            admin_profile.save()

            # Redirect to stored URL or fallback to admin_dashboard
            redirect_url = request.session.pop("redirect_after_profile", None) or "admin_dashboard"
            return redirect(redirect_url)
    else:
        form = AdminProfileForm()

    return render(request, "dashboard/create_admin_profile.html", {"form": form})



# ===================== Sign Up with Email Verification =====================
class SignUpView(CreateView):
    template_name = "accounts/signup.html"
    form_class = CampusSignUpForm
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False  
        user.email_verified = False
        user.save()
        
        self.send_verification_email(user)

        messages.success(
            self.request,
            "✅ Account created. Please verify your email before login."
        )
        return redirect("login")

    def send_verification_email(self, user):
        try:
            current_site = get_current_site(self.request)
            subject = "Verify your CampusConnect Email"
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = email_verification_token.make_token(user)
            verify_url = self.request.build_absolute_uri(
                reverse("verify-email", kwargs={"uidb64": uid, "token": token})
            )
            message = render_to_string("accounts/email_verify.txt", {
                "user": user,
                "verify_url": verify_url,
                "domain": current_site.domain,
            })
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"❌ Email sending failed: {e}")

def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and email_verification_token.check_token(user, token):
        user.email_verified = True
        user.is_active = True
        user.save()
        messages.success(request, "📧 Email verified successfully! You can now log in.")
        return redirect("login")
    else:
        return render(request, "accounts/email_verification_failed.html")
# ===================== Resend Verification =====================
class ResendVerificationView(FormView):
    template_name = "accounts/resend_verification.html"
    success_url = reverse_lazy("login")

    def post(self, request, *args, **kwargs):
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
            if user.email_verified:
                messages.info(request, "✅ Email already verified. You can log in.")
            else:
                signup_view = SignUpView()
                signup_view.request = request
                signup_view.send_verification_email(user)
                messages.success(request, "📩 Verification email resent successfully.")
        except User.DoesNotExist:
            messages.error(request, "❌ No account found with this email.")
        return redirect("login")


# ===================== Admin-only checks =====================
def admin_required(user):
    return user.is_authenticated and user.role == "admin"


# ----------------- Teacher Management -----------------
@login_required
@user_passes_test(admin_required)
def add_teacher(request):
    if request.method == "POST":
        form = TeacherForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Teacher added successfully.")
            return redirect("teacher_list")
        else:
            messages.error(request, "❌ Please correct the errors below.")
    else:
        form = TeacherForm()
    return render(request, "accounts/teachers/add_teacher.html", {"form": form})


@login_required
@user_passes_test(admin_required)
def teacher_list(request):
    teachers = Teacher.objects.all().order_by('session', 'class_name', 'section')
    return render(request, "accounts/teachers/teacher_list.html", {"teachers": teachers})


@login_required
@user_passes_test(admin_required)
def edit_teacher(request, id):
    teacher = get_object_or_404(Teacher, id=id)
    if request.method == "POST":
        form = TeacherForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Teacher updated successfully.")
            return redirect("teacher_list")
    else:
        form = TeacherForm(instance=teacher)
    return render(request, "accounts/teachers/edit_teacher.html", {"form": form, "edit_mode": True})


@login_required
@user_passes_test(admin_required)
def delete_teacher(request, id):
    teacher = get_object_or_404(Teacher, id=id)
    if request.method == "POST":
        teacher.delete()
        messages.success(request, "✅ Teacher deleted successfully.")
        return redirect("teacher_list")
    return render(request, "accounts/teachers/confirm_delete.html", {"object": teacher, "type": "Teacher"})


# ----------------- Student Management -----------------
@login_required
@user_passes_test(admin_required)
def add_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Student added successfully.")
            return redirect('student_list')
        else:
            messages.error(request, "❌ Please correct the errors below.")
    else:
        form = StudentForm()
    return render(request, 'accounts/add_student.html', {'form': form})


@login_required
@user_passes_test(admin_required)
def student_list(request):
    students = Student.objects.all()
    return render(request, 'accounts/student_list.html', {'students': students})


@login_required
@user_passes_test(admin_required)
def edit_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "✏️ Student updated successfully.")
            return redirect("student_list")
    else:
        form = StudentForm(instance=student)
    return render(request, "accounts/edit_student.html", {"form": form})


@login_required
@user_passes_test(admin_required)
def delete_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        student.delete()
        messages.success(request, "✅ Student deleted successfully.")
        return redirect("student_list")
    return render(request, "accounts/delete_student.html", {"student": student})


# ----------------- Role-specific Dashboards -----------------
@login_required
def admin_dashboard(request):
    # Inhe function ke andar import karein
    from academics.models import Course
    from announcements.models import Announcement # Apni sahi app ka naam likhein
    # ... baki models bhi
    
    context = {
        'total_students': Student.objects.count(),
        'total_teachers': Teacher.objects.count(),
        'total_courses': Course.objects.count(),
        'announcements': Announcement.objects.order_by('-created_at')[:5],
    }
    return render(request, 'dashboard/admin_dashboard.html', context)
# Pehle se mojood teacher_dashboard ko is se badal dein
@login_required
def teacher_dashboard(request):
    # 'teacher_profile' underscore ke sath, kyunki aapne model mein yahi related_name diya hai
    from accounts.models import TeacherProfile
    from academics.models import Course, Assignment # Sahi models import karein

    try:
        # User ke sath linked profile dhoondein
        profile = request.user.teacher_profile
        
        # Profile ki class_name ke mutabiq data nikaalein
        courses = Course.objects.filter(teacher=profile)
        
        # Note: 'course' ki jagah 'class_name' use karein agar Assignment model mein 'course' field nahi hai
        assignments = Assignment.objects.filter(
            class_name=profile.class_name
        ).order_by('-created_at')

        context = {
            'courses': courses,
            'assignments': assignments,
            'total_courses': courses.count(),
        }
        return render(request, "accounts/teacher_dashboard.html", context)

    except (TeacherProfile.DoesNotExist, AttributeError):
        # Agar profile nahi hai to error page dikhayein
        from django.http import HttpResponse
        return HttpResponse("<h3>Profile Missing</h3><p>Admin panel mein is user ke liye Teacher Profile banayein.</p>")
@login_required
def student_dashboard(request):
    return render(request, "accounts/student_dashboard.html")
