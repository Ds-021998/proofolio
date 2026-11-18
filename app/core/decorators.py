"""
The access control, in one small file you can read out loud in a demo.

    @login_required
    @role_required("tutor", "coordinator")
    def tutor_mark(request, pk): ...

Two rules, and the whole product rests on the second one:

    1. Every view is behind @login_required.
    2. A Judgement is only ever written by a user in the tutor or coordinator
       group. A student can never create or edit one.

Everything else is queryset filtering: a student's page never queries
anything but their own rows, so there is nothing to leak even if they guess
a URL. Where the existence of a row would itself tell the guesser something,
the view raises Http404 instead of PermissionDenied.
"""

from functools import wraps

from django.core.exceptions import PermissionDenied


def role_required(*roles):
    """Allow only users in one of the named Django Groups."""

    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied
            if not request.user.groups.filter(name__in=roles).exists():
                raise PermissionDenied
            return view(request, *args, **kwargs)

        return wrapper

    return decorator
