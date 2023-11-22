# decorators.py
from functools import wraps
from django.shortcuts import redirect

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_admin():
            return view_func(request, *args, **kwargs)
        else:
            return redirect('/myapp/login/')  # Redirect to an access denied page or login page
    return _wrapped_view

def patient_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_patient():
            return view_func(request, *args, **kwargs)
        else:
            return redirect('/myapp/login/')
    return _wrapped_view

def doctor_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_doctor():
            return view_func(request, *args, **kwargs)
        else:
            return redirect('/myapp/login/')  # Redirect to an access denied page or login page
    return _wrapped_view

