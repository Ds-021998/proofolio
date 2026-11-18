"""
Proofolio — views.

Two rules hold across the whole file, and between them they are the product:

    1. Every view is @login_required.
    2. A Judgement is only ever written by a user in the tutor or coordinator
       group, which is what @role_required enforces.

Everything else is queryset filtering. A student's page never queries anything
but their own rows, so there is nothing to leak even if they guess a URL.
Where the existence of a row would itself tell the guesser something, the view
raises Http404 rather than PermissionDenied.
"""

import datetime

from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import SignUpForm

from .context_processors import ROLE_HOMES, role_of
from .decorators import role_required
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
    Verdict,
)


# ======================================================================
# Helpers
# ======================================================================

def current_course(user):
    enrolment = user.enrolments.select_related("course").first()
    return enrolment.course if enrolment else None


def tutorial_group(user):
    enrolment = user.enrolments.first()
    return enrolment.tutorial_group if enrolment else ""


def history_by_title(student, course):
    """Every released judgement this student has, grouped by criterion title.

    The same criterion appears on more than one assessment, so the title is
    what ties them together. Each list is ordered oldest to newest, and that
    ordering is what makes a record a record rather than a grade.
    """
    judgements = (
        Judgement.objects
        .filter(submission__student=student,
                submission__assessment__course=course,
                submission__released_at__isnull=False)
        .select_related("criterion", "submission__assessment")
        .order_by("submission__assessment__order", "created_at")
    )
    history = {}
    for j in judgements:
        history.setdefault(j.criterion.title, []).append(j)
    return history


def is_open(history, title):
    """A criterion is open if its most recent judgement is not `met`.

    One rule, and it powers the carry-forward, the record and the meter.
    Never judged counts as open: nobody has verified it yet.
    """
    judgements = history.get(title)
    if not judgements:
        return True
    return judgements[-1].verdict != Verdict.MET


def paragraphs(text):
    return [p.strip() for p in text.splitlines() if p.strip()]


def percent(value, total):
    return round(100 * value / total) if total else 0


# ======================================================================
# Entry
# ======================================================================

def landing(request):
    """The public front page. No login, no queries, nothing to leak."""
    return render(request, "landing.html")


def signup(request):
    """Student self-registration.

    Three things happen here and the order matters:
      1. the account is created,
      2. it is put in the `student` group — never anything else,
      3. it is enrolled in the course the join code resolved to.

    Step 2 is not a field on the form. A user cannot choose to be a marker,
    because a marker is the only person who can write a judgement.
    """
    if request.user.is_authenticated:
        return redirect("post_login")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                student_group, _ = Group.objects.get_or_create(name="student")
                user.groups.set([student_group])
                Enrolment.objects.get_or_create(
                    user=user, course=form.course,
                    defaults=dict(tutorial_group=""),
                )
            auth_login(request, user)
            messages.success(
                request,
                f"Welcome to {form.course.code}. Your criteria are below — "
                "they were published before the assignment opened.",
            )
            return redirect("post_login")
    else:
        form = SignUpForm()

    return render(request, "registration/signup.html", {"form": form})


@login_required
def post_login(request):
    """One account, one role, one home."""
    role = role_of(request.user)
    if role is None:
        messages.warning(request, "Your account has no role yet. Ask your coordinator to add you to a course.")
        return redirect("login")
    return redirect(ROLE_HOMES[role])


def error_403(request, exception=None):
    return render(request, "errors/403.html", status=403)


def error_404(request, exception=None):
    return render(request, "errors/404.html", status=404)


# ======================================================================
# Student
#
# No student id appears in any URL on this side of the app. Every queryset
# below filters on request.user, so there is nothing to tamper with.
# ======================================================================

@login_required
@role_required("student")
def student_dashboard(request):
    course = current_course(request.user)
    if course is None:
        return render(request, "student/dashboard.html", {"nav": "home", "total_count": 0,
                                                          "verified_count": 0, "open_criteria": []})

    next_assessment = (Assessment.objects
                       .filter(course=course, is_published=True)
                       .order_by("-order").first())
    criteria = list(next_assessment.criteria.filter(is_published=True)) if next_assessment else []
    history = history_by_title(request.user, course)

    open_criteria = []
    segments = []
    for c in criteria:
        if is_open(history, c.title):
            segments.append("open")
            past = history.get(c.title)
            c.verdict = past[-1].verdict if past else None
            c.open_since = past[-1].submission.assessment.title if past else ""
            open_criteria.append(c)
        else:
            segments.append("ok")

    covered = set(TutorialCoverage.objects
                  .filter(criterion__assessment=next_assessment,
                          tutorial_group=tutorial_group(request.user))
                  .values_list("criterion__title", flat=True))
    note = None
    for c in open_criteria:
        if c.title in covered:
            note = f"This week's tutorial is covering {c.title} — one of yours."
            break

    context = {
        "nav": "home",
        "verified_count": len(criteria) - len(open_criteria),
        "total_count": len(criteria),
        "meter_segments": segments,
        "next_assessment": next_assessment,
        "open_criteria": open_criteria,
        "tutorial_note": note,
        "current_assessment_id": next_assessment.id if next_assessment else None,
        "current_assessment_title": next_assessment.title if next_assessment else "",
    }
    return render(request, "student/dashboard.html", context)


@login_required
@role_required("student")
def student_assessment(request, pk):
    course = current_course(request.user)
    assessment = get_object_or_404(Assessment, pk=pk, course=course, is_published=True)
    submission = Submission.objects.filter(student=request.user, assessment=assessment).first()
    criteria = list(assessment.criteria.filter(is_published=True))
    history = history_by_title(request.user, course)

    if request.method == "POST" and submission is None:
        text = request.POST.get("text", "").strip()
        if not text:
            messages.error(request, "Add your submission text before submitting.")
        else:
            submission = Submission.objects.create(student=request.user, assessment=assessment, text=text)
            for c in criteria:
                # A pointer is a pointer. It is never written to a Judgement,
                # and the marker is free to ignore it.
                pointer = request.POST.get(f"pointer-{c.id}", "").strip()
                if pointer:
                    Pointer.objects.create(submission=submission, criterion=c, text=pointer[:200])
            messages.success(request, "Submitted. Your marker sees the criteria you were pointed at.")
            return redirect("student_assessment", pk=pk)

    for c in criteria:
        # Carried in = still open from a previous assessment.
        c.carried_in = is_open(history, c.title) and bool(history.get(c.title))
        c.pointer = submission.pointer_for(c) if submission else ""

    context = {
        "nav": "submit",
        "assessment": assessment,
        "criteria": criteria,
        "submission": submission,
        "feedback_ready": bool(submission and submission.is_released),
        "feedback_url": f"/assessment/{pk}/feedback/",
        "current_assessment_id": assessment.id,
        "current_assessment_title": assessment.title,
    }
    return render(request, "student/assessment.html", context)


@login_required
@role_required("student")
def student_feedback(request, pk):
    course = current_course(request.user)
    assessment = get_object_or_404(Assessment, pk=pk, course=course)
    submission = Submission.objects.filter(student=request.user, assessment=assessment,
                                           released_at__isnull=False).first()
    if submission is None:
        messages.info(request, "Nothing released for that assessment yet.")
        return redirect("student_dashboard")

    history = history_by_title(request.user, course)
    lines = paragraphs(submission.text)
    results, closed_count = [], 0

    for j in submission.judgements.select_related("criterion").order_by("criterion__order"):
        c = j.criterion
        past = [p for p in history.get(c.title, []) if p.id != j.id]
        before = past[-1].verdict if past else None

        # This comparison is the demo: the same criterion, judged twice.
        if before and before != Verdict.MET and j.verdict == Verdict.MET:
            change = "closed"
        elif before and before != Verdict.MET and j.verdict != Verdict.MET:
            change = "still_open"
        elif before == Verdict.MET and j.verdict != Verdict.MET:
            change = "newly_open"
        else:
            change = ""

        if j.verdict == Verdict.MET:
            closed_count += 1

        c.verdict = j.verdict
        c.change = change
        c.comment = j.comment
        c.verified_on = j.created_at
        c.para_number = min(c.order, len(lines)) or 1
        c.quote = lines[c.para_number - 1] if lines else ""
        results.append(c)

    questions = []
    for q in submission.questions.select_related("criterion"):
        questions.append({"criterion_title": q.criterion.title, "text": q.student_text,
                          "reply": q.reply, "answered_at": q.answered_at})

    context = {
        "nav": "feedback",
        "assessment": assessment,
        "released_at": submission.released_at,
        "closed_count": closed_count,
        "results": results,
        "my_questions": questions,
        "current_assessment_id": assessment.id,
        "current_assessment_title": assessment.title,
    }
    return render(request, "student/feedback.html", context)


@login_required
@role_required("student")
def student_record(request):
    course = current_course(request.user)
    history = history_by_title(request.user, course) if course else {}

    capabilities, closed_count, open_count = [], 0, 0
    for title, judgements in history.items():
        last = judgements[-1]
        if last.verdict == Verdict.MET:
            closed_count += 1
        else:
            open_count += 1
        capabilities.append({
            "name": last.criterion.capability_name,
            "criterion_title": title,
            "sfia_code": last.criterion.sfia_code,
            "latest_verdict": last.verdict,
            "events": [{"assessment_title": j.submission.assessment.title,
                        "verdict": j.verdict,
                        "created_at": j.created_at,
                        "verified_by": j.verified_by} for j in judgements],
        })

    latest = Assessment.objects.filter(course=course, is_published=True).order_by("-order").first()
    context = {
        "nav": "record",
        "capabilities": capabilities,
        "closed_count": closed_count,
        "open_count": open_count,
        "current_assessment_id": latest.id if latest else None,
        "current_assessment_title": latest.title if latest else "",
    }
    return render(request, "student/record.html", context)


@login_required
@role_required("student")
def student_export_preview(request):
    """Only closed capabilities travel, and the trajectory travels with them.

    The improvement is the point, so "not met in August, met in September" is
    the claim — not "met".
    """
    course = current_course(request.user)
    history = history_by_title(request.user, course) if course else {}

    capabilities, withheld = [], 0
    for title, judgements in history.items():
        last = judgements[-1]
        if last.verdict != Verdict.MET:
            withheld += 1
            continue
        first = judgements[0]
        span = {j.submission.assessment.title for j in judgements}
        capabilities.append({
            "name": last.criterion.capability_name,
            "first_verdict": first.verdict,
            "first_verdict_date": first.created_at,
            "closed_date": last.created_at,
            "assessment_span": f"{len(span)} assessment{'s' if len(span) != 1 else ''}",
        })

    return render(request, "student/export_preview.html",
                  {"nav": "record", "capabilities": capabilities, "withheld_count": withheld})


@login_required
@role_required("student")
def student_ask(request, criterion_id):
    course = current_course(request.user)
    criterion = get_object_or_404(Criterion, pk=criterion_id, assessment__course=course)
    submission = get_object_or_404(Submission, student=request.user,
                                   assessment=criterion.assessment, released_at__isnull=False)
    judgement = submission.judgements.filter(criterion=criterion).first()

    if request.method == "POST":
        text = request.POST.get("text", "").strip()
        if text:
            Question.objects.create(submission=submission, criterion=criterion, student_text=text)
            messages.success(request, "Sent. Your marker sees which criterion you're asking about.")
            return redirect("student_feedback", pk=criterion.assessment_id)
        messages.error(request, "Write your question before sending.")

    criterion.verdict = judgement.verdict if judgement else None
    context = {
        "nav": "feedback",
        "criterion": criterion,
        "assessment_id": criterion.assessment_id,
        "marker_comment": judgement.comment if judgement else "",
        "current_assessment_id": criterion.assessment_id,
        "current_assessment_title": criterion.assessment.title,
    }
    return render(request, "student/ask.html", context)


# ======================================================================
# Tutor
# ======================================================================

def _tutor_nav_counts(user, course):
    group = tutorial_group(user)
    to_mark = Submission.objects.filter(assessment__course=course, released_at__isnull=True,
                                        student__enrolments__tutorial_group=group).count()
    open_q = Question.objects.filter(submission__assessment__course=course,
                                     answered_at__isnull=True,
                                     submission__student__enrolments__tutorial_group=group).count()
    return to_mark, open_q


@login_required
@role_required("tutor", "coordinator")
def tutor_queue(request):
    course = current_course(request.user)
    group = tutorial_group(request.user)
    assessment = Assessment.objects.filter(course=course, is_published=True).order_by("-order").first()

    waiting = []
    if assessment:
        qs = (Submission.objects
              .filter(assessment=assessment, released_at__isnull=True,
                      student__enrolments__tutorial_group=group)
              .order_by("submitted_at"))
        for i, s in enumerate(qs, start=1):
            s.position = i
            waiting.append(s)

    done = Submission.objects.filter(assessment=assessment, released_at__isnull=False,
                                     student__enrolments__tutorial_group=group).count() if assessment else 0
    to_mark, open_q = _tutor_nav_counts(request.user, course)
    return render(request, "tutor/queue.html",
                  {"nav": "mark", "assessment": assessment, "waiting": waiting,
                   "done_count": done, "to_mark": to_mark, "open_q": open_q})


@login_required
@role_required("tutor", "coordinator")
def tutor_mark(request, pk):
    course = current_course(request.user)
    group = tutorial_group(request.user)

    # A submission outside this tutor's group 404s. A 403 would confirm it exists.
    submission = get_object_or_404(Submission, pk=pk, assessment__course=course,
                                   student__enrolments__tutorial_group=group)
    criteria = list(submission.assessment.criteria.filter(is_published=True))
    existing = {j.criterion_id: j for j in submission.judgements.all()}

    if request.method == "POST":
        for c in criteria:
            verdict = request.POST.get(f"verdict-{c.id}")
            if verdict not in Verdict.values:
                continue
            comment = request.POST.get(f"comment-{c.id}", "").strip()
            if verdict != Verdict.MET and not comment:
                comment = c.prefilled_comment
            Judgement.objects.update_or_create(
                submission=submission, criterion=c,
                defaults=dict(verdict=verdict,
                              comment="" if verdict == Verdict.MET else comment,
                              marker=request.user),
            )
            indicator = request.POST.get(f"indicator-{c.id}", "").strip()
            if indicator:
                Indicator.objects.get_or_create(criterion=c, text=indicator[:300],
                                                defaults=dict(contributed_by=request.user))

        # Time accrues here, where nobody can see it, and surfaces only in
        # this tutor's own aggregate view.
        started = request.session.pop(f"mark_start_{pk}", None)
        if started:
            elapsed = int(timezone.now().timestamp() - started)
            submission.marking_seconds += max(0, min(elapsed, 3 * 3600))

        judged = submission.judgements.count()
        if request.POST.get("action") == "release":
            if judged < len(criteria):
                messages.error(request, "Judge every criterion before releasing.")
            else:
                submission.released_at = timezone.now()
                messages.success(request, "Released. The student sees what changed since last time.")
        else:
            messages.success(request, "Judgements saved.")
        submission.save()
        if submission.is_released:
            return redirect("tutor_queue")
        return redirect("tutor_mark", pk=pk)

    request.session.setdefault(f"mark_start_{pk}", timezone.now().timestamp())

    lines = paragraphs(submission.text)
    judged_count = 0
    for c in criteria:
        j = existing.get(c.id)
        c.verdict = j.verdict if j else None
        c.comment = j.comment if j and j.comment else c.prefilled_comment
        c.indicator = ""
        c.pointer = submission.pointer_for(c)
        c.para_label = f"P{min(c.order, len(lines)) or 1}"
        if j:
            judged_count += 1

    flagged = {min(c.order, len(lines)) for c in criteria if c.verdict and c.verdict != Verdict.MET}
    submission.text_paragraphs = [{"text": t, "flagged": (i + 1) in flagged} for i, t in enumerate(lines)]
    peers = list(Submission.objects.filter(assessment=submission.assessment)
                 .order_by("submitted_at").values_list("id", flat=True))
    submission.position = peers.index(submission.id) + 1 if submission.id in peers else 1
    submission.cohort_size = len(peers)

    to_mark, open_q = _tutor_nav_counts(request.user, course)
    return render(request, "tutor/marking.html",
                  {"nav": "mark", "submission": submission, "criteria": criteria,
                   "judged_count": judged_count, "can_release": judged_count == len(criteria),
                   "to_mark": to_mark, "open_q": open_q})


@login_required
@role_required("tutor", "coordinator")
def tutor_brief(request):
    """Nobody writes this. It is what the marking already said, counted."""
    course = current_course(request.user)
    group = tutorial_group(request.user)
    last_marked = (Assessment.objects
                   .filter(course=course, submissions__released_at__isnull=False)
                   .order_by("-order").distinct().first())

    bars, top = [], None
    group_size = Enrolment.objects.filter(course=course, tutorial_group=group,
                                          user__groups__name="student").count()
    if last_marked:
        total = Submission.objects.filter(assessment=last_marked, released_at__isnull=False,
                                          student__enrolments__tutorial_group=group).count()
        rows = []
        for c in last_marked.criteria.all():
            missed = Judgement.objects.filter(
                criterion=c, submission__released_at__isnull=False,
                submission__student__enrolments__tutorial_group=group,
            ).exclude(verdict=Verdict.MET).count()
            rows.append((c, missed, total))
        rows.sort(key=lambda r: -r[1])

        for c, missed, tot in rows:
            bars.append({"label": c.title, "value": missed, "total": tot,
                         "percent": percent(missed, tot), "sub": ""})
        if rows and rows[0][1]:
            c = rows[0][0]
            bars[0]["sub"] = "Most missed in your group"
            examples = []
            for j in Judgement.objects.filter(
                criterion=c, submission__student__enrolments__tutorial_group=group
            ).exclude(verdict=Verdict.MET).select_related("submission")[:3]:
                # De-identified: the sentence, never the student.
                lines = paragraphs(j.submission.text)
                if lines:
                    examples.append(lines[min(c.order, len(lines)) - 1])
            top = {"id": c.id, "title": c.title, "capability_name": c.capability_name,
                   "examples": examples, "opener": c.good_looks_like,
                   "covered": TutorialCoverage.objects.filter(criterion=c, tutorial_group=group).exists()}

    to_mark, open_q = _tutor_nav_counts(request.user, course)
    return render(request, "tutor/brief.html",
                  {"nav": "brief", "group_size": group_size, "bars": bars, "top": top,
                   "tutorial_date": timezone.localdate() + datetime.timedelta(days=2),
                   "to_mark": to_mark, "open_q": open_q})


@login_required
@role_required("tutor", "coordinator")
def tutor_mark_covered(request, criterion_id):
    criterion = get_object_or_404(Criterion, pk=criterion_id,
                                  assessment__course=current_course(request.user))
    TutorialCoverage.objects.get_or_create(criterion=criterion,
                                           tutorial_group=tutorial_group(request.user))
    messages.success(request, "Marked as covered. Your coordinator sees that it happened, not who taught what.")
    return redirect("tutor_brief")


@login_required
@role_required("tutor", "coordinator")
def tutor_questions(request):
    course = current_course(request.user)
    group = tutorial_group(request.user)
    qs = (Question.objects
          .filter(submission__assessment__course=course,
                  submission__student__enrolments__tutorial_group=group)
          .select_related("criterion", "submission"))

    def row(q, i):
        return {"id": q.id, "criterion_title": q.criterion.title,
                "student_label": f"Script {i}", "text": q.student_text,
                # Pre-drafted from the standard the coordinator already wrote.
                "draft_reply": q.criterion.good_looks_like,
                "reply": q.reply, "answered_at": q.answered_at}

    waiting = [row(q, i) for i, q in enumerate(qs.filter(answered_at__isnull=True), 1)]
    answered = [row(q, i) for i, q in enumerate(qs.filter(answered_at__isnull=False), 1)]

    to_mark, open_q = _tutor_nav_counts(request.user, course)
    return render(request, "tutor/questions.html",
                  {"nav": "questions", "waiting": waiting, "answered": answered,
                   "to_mark": to_mark, "open_q": open_q})


@login_required
@role_required("tutor", "coordinator")
def tutor_answer(request, pk):
    """Answering never reopens the script."""
    question = get_object_or_404(Question, pk=pk,
                                 submission__assessment__course=current_course(request.user))
    if request.method == "POST":
        reply = request.POST.get("reply", "").strip()
        if reply:
            question.reply = reply
            question.answered_at = timezone.now()
            question.save()
            messages.success(request, "Replied.")
    return redirect("tutor_questions")


@login_required
@role_required("tutor", "coordinator")
def tutor_time(request):
    """Aggregate, after the fact, to this tutor only.

    No per-script breakdown is queried here and none is shown, so there is
    nothing for anyone to ask for.
    """
    course = current_course(request.user)
    marked = Submission.objects.filter(judgements__marker=request.user,
                                       assessment__course=course).distinct()
    seconds = sum(s.marking_seconds for s in marked)
    scripts = marked.count()
    hours = seconds / 3600
    paid = 7.0

    to_mark, open_q = _tutor_nav_counts(request.user, course)
    return render(request, "tutor/time.html", {
        "nav": "time",
        "hours_marked": f"{hours:.1f}",
        "scripts_marked": scripts,
        "average_minutes": round(seconds / 60 / scripts) if scripts else 0,
        "paid_hours": f"{paid:.1f}",
        "over_allocation": hours > paid,
        "difference": f"{abs(hours - paid):.1f}",
        "to_mark": to_mark, "open_q": open_q,
    })


# ======================================================================
# Coordinator
# ======================================================================

@login_required
@role_required("coordinator")
def coordinator_criteria(request):
    course = current_course(request.user)
    assessment = Assessment.objects.filter(course=course).order_by("-order").first()
    criteria = list(assessment.criteria.prefetch_related("indicators")) if assessment else []
    return render(request, "coordinator/criteria.html",
                  {"nav": "criteria", "assessment": assessment, "criteria": criteria,
                   "sfia_draft": True})


@login_required
@role_required("coordinator")
def coordinator_criterion_edit(request, pk):
    course = current_course(request.user)
    criterion = get_object_or_404(Criterion, pk=pk, assessment__course=course)
    if request.method == "POST":
        for field in ("title", "capability_name", "sfia_code", "clause",
                      "good_looks_like", "prefilled_comment"):
            setattr(criterion, field, request.POST.get(field, "").strip())
        criterion.is_published = bool(request.POST.get("is_published"))
        criterion.save()
        messages.success(request, "Criterion saved.")
        return redirect("coordinator_criteria")
    return render(request, "coordinator/criterion_edit.html",
                  {"nav": "criteria", "criterion": criterion, "assessment": criterion.assessment})


@login_required
@role_required("coordinator")
def coordinator_cohort(request):
    """Aggregated across the cohort. No student and no marker is named."""
    course = current_course(request.user)
    last_marked = (Assessment.objects
                   .filter(course=course, submissions__released_at__isnull=False)
                   .order_by("-order").distinct().first())

    bars = []
    if last_marked:
        total = Submission.objects.filter(assessment=last_marked, released_at__isnull=False).count()
        for c in last_marked.criteria.all():
            missed = Judgement.objects.filter(criterion=c, submission__released_at__isnull=False) \
                                      .exclude(verdict=Verdict.MET).count()
            bars.append({"label": c.title, "value": missed, "total": total,
                         "percent": percent(missed, total), "sub": ""})
        bars.sort(key=lambda b: -b["value"])

    covered = list(TutorialCoverage.objects.filter(criterion__assessment__course=course)
                   .values_list("criterion__title", flat=True).distinct())

    return render(request, "coordinator/cohort.html", {
        "nav": "cohort",
        "cohort_size": Enrolment.objects.filter(course=course, user__groups__name="student").count(),
        "weeks_remaining": 4,
        "bars": bars,
        "covered": covered,
    })


@login_required
@role_required("coordinator")
def coordinator_handover(request):
    """Indicators and notes attach to the criterion, not to the person who
    wrote them. That is what makes them survive tutor turnover."""
    course = current_course(request.user)
    assessment = Assessment.objects.filter(course=course).order_by("-order").first()

    if request.method == "POST" and assessment:
        text = request.POST.get("text", "").strip()
        if text:
            HandoverNote.objects.create(assessment=assessment, text=text, author=request.user)
            messages.success(request, "Note saved against the assessment.")
        return redirect("coordinator_handover")

    criteria = []
    for c in Criterion.objects.filter(assessment__course=course).prefetch_related("indicators"):
        items = list(c.indicators.all())
        if items:
            criteria.append(c)

    notes = HandoverNote.objects.filter(assessment__course=course) if assessment else []
    return render(request, "coordinator/handover.html",
                  {"nav": "handover", "criteria_with_indicators": criteria, "notes": notes})
