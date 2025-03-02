from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib import messages


def admin_required(view_func):
    """
    Decorator to ensure that the user is an admin.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if user is authenticated and is an admin
        if request.user.is_authenticated and request.user.is_superuser:
            # User is an admin, allow access to the view
            return view_func(request, *args, **kwargs)
        else:
            messages.warning(request, 'You are not authorized as an admin.')
            # User is not an admin, log them out and redirect to login page
            logout(request)
            return redirect('customerlogin')

    return _wrapped_view
