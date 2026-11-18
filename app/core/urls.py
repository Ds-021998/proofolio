"""
URL names used by the templates.

Every {% url %} in the template pack resolves against this file, so drop it in
as-is and the templates render. a teammate writes the views; the names and
signatures below are the contract between the two halves.

Wire it up in proofolio/urls.py:

    from django.contrib import admin
    from django.urls import path, include

    urlpatterns = [
        path("admin/", admin.site.urls),
        path("", include("django.contrib.auth.urls")),   # login, logout
        path("", include("core.urls")),
    ]
"""

from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    # Django's own login view, with one setting changed: someone who is
    # already signed in gets sent to their home instead of a login form
    # with their own name in the header.
    path("login/", auth_views.LoginView.as_view(redirect_authenticated_user=True), name="login"),

    # Public marketing page. Anyone can see it, signed in or not.
    path("", views.landing, name="landing"),

    # Student self-registration. Always creates a student; see core/forms.py.
    path("signup/", views.signup, name="signup"),

    # Sends each role to its own home after login.
    path("go/", views.post_login, name="post_login"),

    # ---- student -------------------------------------------------------
    path("home/", views.student_dashboard, name="student_dashboard"),
    path("assessment/<int:pk>/", views.student_assessment, name="student_assessment"),
    path("assessment/<int:pk>/feedback/", views.student_feedback, name="student_feedback"),
    path("record/", views.student_record, name="student_record"),
    path("record/preview/", views.student_export_preview, name="student_export_preview"),
    path("ask/<int:criterion_id>/", views.student_ask, name="student_ask"),

    # ---- tutor ---------------------------------------------------------
    path("marking/", views.tutor_queue, name="tutor_queue"),
    path("marking/<int:pk>/", views.tutor_mark, name="tutor_mark"),
    path("brief/", views.tutor_brief, name="tutor_brief"),
    path("brief/<int:criterion_id>/covered/", views.tutor_mark_covered, name="tutor_mark_covered"),
    path("questions/", views.tutor_questions, name="tutor_questions"),
    path("questions/<int:pk>/answer/", views.tutor_answer, name="tutor_answer"),
    path("my-time/", views.tutor_time, name="tutor_time"),

    # ---- coordinator ---------------------------------------------------
    path("criteria/", views.coordinator_criteria, name="coordinator_criteria"),
    path("criteria/<int:pk>/edit/", views.coordinator_criterion_edit, name="coordinator_criterion_edit"),
    path("cohort/", views.coordinator_cohort, name="coordinator_cohort"),
    path("handover/", views.coordinator_handover, name="coordinator_handover"),
]
