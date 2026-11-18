"""
Context the templates expect on EVERY page, supplied once instead of in each
view. Register it in settings.py:

    TEMPLATES = [{
        ...
        "OPTIONS": {"context_processors": [
            ...,
            "core.context_processors.proofolio",
        ]},
    }]

What it provides
    role          "student" | "tutor" | "coordinator" — drives the nav and the
                  avatar colour. Read from Django's Groups, which is also what
                  the permission checks read, so the interface and the rules
                  can never disagree.
    role_label    human-readable, used in aria-labels and the 403 page
    course        the user's current Course
    home_url      where "Go home" goes for this role
"""

from django.conf import settings
from django.urls import reverse


ROLE_LABELS = {
    "student": "Student",
    "tutor": "Sessional marker",
    "coordinator": "Course coordinator",
}

ROLE_HOMES = {
    "student": "student_dashboard",
    "tutor": "tutor_brief",
    "coordinator": "coordinator_criteria",
}


def role_of(user):
    """One role per account. First match wins, most privileged first."""
    if not user.is_authenticated:
        return None
    names = set(user.groups.values_list("name", flat=True))
    for r in ("coordinator", "tutor", "student"):
        if r in names:
            return r
    return None


def proofolio(request):
    role = role_of(request.user)
    if role is None:
        return {"role": None, "role_label": "", "course": None, "home_url": "/",
                "show_demo_logins": settings.SHOW_DEMO_LOGINS}

    enrolment = request.user.enrolments.select_related("course").first()
    course = enrolment.course if enrolment else None

    return {
        "role": role,
        "role_label": ROLE_LABELS[role],
        "course": course,
        "home_url": reverse(ROLE_HOMES[role]),
        "show_demo_logins": settings.SHOW_DEMO_LOGINS,
    }
