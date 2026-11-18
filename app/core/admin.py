"""
Register every model so /admin is a working interface from day one.

This is the coordinator's back door while the real screens are being built,
and it's how a tutor can be given a judgement to look at before the marking
screen is finished. Zero code for a usable CRUD interface is the main reason
we picked Django.
"""

from django.contrib import admin

from .models import (
    Assessment,
    Course,
    Criterion,
    Enrolment,
    HandoverNote,
    Indicator,
    Judgement,
    Pointer,
    Question,
    Submission,
    TutorialCoverage,
)


class CriterionInline(admin.TabularInline):
    model = Criterion
    extra = 0
    fields = ("order", "title", "capability_name", "is_published")


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("code", "name")


@admin.register(Enrolment)
class EnrolmentAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "tutorial_group")
    list_filter = ("course", "tutorial_group")


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order", "due_date", "is_published")
    list_filter = ("course", "is_published")
    inlines = [CriterionInline]


@admin.register(Criterion)
class CriterionAdmin(admin.ModelAdmin):
    list_display = ("title", "capability_name", "assessment", "is_published")
    list_filter = ("assessment", "is_published")
    search_fields = ("title", "capability_name")


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("student", "assessment", "submitted_at", "released_at", "marking_seconds")
    list_filter = ("assessment",)


@admin.register(Judgement)
class JudgementAdmin(admin.ModelAdmin):
    list_display = ("criterion", "verdict", "marker", "submission", "created_at")
    list_filter = ("verdict", "criterion__assessment")


admin.site.register([Pointer, Question, Indicator, HandoverNote, TutorialCoverage])

admin.site.site_header = "Proofolio admin"
admin.site.site_title = "Proofolio"
admin.site.index_title = "Course data"
