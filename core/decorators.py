
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def admin_required(view_func):

    @login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        is_admin = (
            request.user.is_superuser
            or request.user.groups.filter(name__iexact='admin').exists()
        )

        if not is_admin:
            raise PermissionDenied

        return view_func(request, *args, **kwargs)

    return wrapper
