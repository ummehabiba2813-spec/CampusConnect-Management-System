from functools import wraps
from django.http import HttpResponseForbidden
from django.utils.decorators import method_decorator


def role_required(*roles):
    """
    Restrict access based on user role(s).
    Usage:
        @role_required("ADMIN", "TEACHER")
        def my_view(request): ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.role in roles:
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("You do not have permission to access this page.")
        return _wrapped
    return decorator


# ✅ Example usage in Function-Based View (FBV)
@role_required("ADMIN")
def admin_dashboard(request):
    return HttpResponse("Welcome Admin Dashboard!")


# ✅ Example usage in Class-Based View (CBV)
from django.views import View
from django.http import HttpResponse

@method_decorator(role_required("ADMIN"), name="dispatch")
class AdminOnlyView(View):
    def get(self, request):
        return HttpResponse("Welcome, Admin!")
