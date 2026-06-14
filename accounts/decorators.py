from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
def role_required(allowed_roles=[]):
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]
        
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, "Silakan login terlebih dahulu untuk mengakses halaman ini.")
                return redirect('login')
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            if request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, "Anda tidak memiliki wewenang untuk mengakses halaman ini!")
                return redirect('dashboard')
                
        return _wrapped_view
    return decorator
