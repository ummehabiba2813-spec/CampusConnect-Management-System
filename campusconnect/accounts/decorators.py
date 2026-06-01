from django.http import JsonResponse
from functools import wraps

def role_required(allowed_roles=None):
    if allowed_roles is None:
        allowed_roles = []

    # ensure allowed_roles is list (even if single string diya ho)
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]

    allowed_roles = [role.lower() for role in allowed_roles]  # case-insensitive

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({"error": "Authentication required"}, status=401)

            user_role = (request.user.role or "").lower()  # avoid NoneType
            if user_role not in allowed_roles:
                return JsonResponse({"error": "Permission denied"}, status=403)

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
