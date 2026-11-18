"""
Proofolio — the data model.

Nine tables. Eight of them are the ones in the build plan; `Enrolment` is the
ninth, and it exists because two questions need answering that nothing else
could answer: which course is this student in, and which tutorial group does
this tutor mark?

The one rule the whole product rests on:

    A Judgement is only ever created by a user in the tutor or coordinator
    group. A student can never create or edit one.

Everything else follows from that. A criterion is "open" for a student if
their most recent Judgement on it is not `met` — one query, and it powers the
carry-forward, the record and the progress view.
"""

from django.conf import settings
from django.db import models


class Verdict(models.TextChoices):
    MET = "met", "Met"
    PARTLY = "partly", "Partly met"
    NOT_MET = "not_met", "Not met"


class Course(models.Model):
    code = models.CharField(max_length=20, unique=True)      # COMP7110
    name = models.CharField(max_length=200)

    # Students self-enrol with this. The coordinator hands it out; it is not
    # guessable from the course code, and it is the only way a new account
    # gets attached to a course.
    join_code = models.CharField(max_length=20, unique=True, blank=True, null=True)

    def __str__(self):
        return f"{self.code} {self.name}"


class Enrolment(models.Model):
    """Who is in this course, and which tutorial group they belong to.

    A tutor is enrolled too, with the group they mark. That is how
    `tutor_queue` knows which twenty scripts are theirs.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrolments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrolments")
    tutorial_group = models.CharField(max_length=20, blank=True)   # "T03"

    class Meta:
        unique_together = [("user", "course")]

    def __str__(self):
        return f"{self.user} in {self.course.code} ({self.tutorial_group or 'no group'})"


class Assessment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="assessments")
    title = models.CharField(max_length=200)                  # "Assignment 2"
    due_date = models.DateField()
    is_published = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=1)            # 1, 2, 3 — the record needs a sequence

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.course.code} — {self.title}"


class Criterion(models.Model):
    """The shared object. Everything in Proofolio hangs off this.

    Written once by the coordinator, then used at four moments:
      clause            → shown to the student before they write
      good_looks_like   → shown to the student, and seeds the question reply
      prefilled_comment → attaches itself when a marker judges partly/not met
      capability_name   → the line in the student's record
    """

    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name="criteria")
    title = models.CharField(max_length=300)
    capability_name = models.CharField(max_length=120)
    sfia_code = models.CharField(max_length=20, blank=True)   # draft mapping, labelled as draft in the UI
    clause = models.TextField()
    good_looks_like = models.TextField()
    prefilled_comment = models.TextField()
    what_to_do = models.TextField(blank=True)
    is_published = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["order"]
        verbose_name_plural = "criteria"

    def __str__(self):
        return self.title


class Submission(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="submissions")
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name="submissions")
    text = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    released_at = models.DateTimeField(null=True, blank=True)

    # Accrued server-side while a marker works. Never rendered on the marking
    # screen — a visible timer reads as surveillance. It surfaces only in that
    # tutor's own aggregate "My time" view.
    marking_seconds = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = [("student", "assessment")]
        ordering = ["submitted_at"]

    def __str__(self):
        return f"{self.student} — {self.assessment.title}"

    @property
    def is_released(self):
        return self.released_at is not None

    def pointer_for(self, criterion):
        p = self.pointers.filter(criterion=criterion).first()
        return p.text if p else ""


class Pointer(models.Model):
    """Where the student says they addressed a carried-in criterion.

    A pointer, not a claim. It is never written to a Judgement, and the
    marker is free to ignore it. This replaced the self-certification
    checkbox the coordinator rejected.
    """

    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name="pointers")
    criterion = models.ForeignKey(Criterion, on_delete=models.CASCADE, related_name="pointers")
    text = models.CharField(max_length=200)

    class Meta:
        unique_together = [("submission", "criterion")]


class Judgement(models.Model):
    """The core table. This row is the attestation.

    Created only by a user in the tutor or coordinator group — enforced by
    @role_required on every view that writes one.
    """

    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name="judgements")
    criterion = models.ForeignKey(Criterion, on_delete=models.CASCADE, related_name="judgements")
    verdict = models.CharField(max_length=10, choices=Verdict.choices)
    comment = models.TextField(blank=True)
    marker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="judgements")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("submission", "criterion")]
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.criterion} → {self.get_verdict_display()}"

    @property
    def closes(self):
        return self.verdict == Verdict.MET

    @property
    def verified_by(self):
        # The team, never the individual marker. That removes the personal
        # pressure on a casual tutor who faces that student on Thursday.
        return f"{self.submission.assessment.course.code} teaching team"


class Question(models.Model):
    """Always anchored to a criterion — that anchoring is what lets the
    tutor's reply be pre-drafted, and why the script is never reopened."""

    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name="questions")
    criterion = models.ForeignKey(Criterion, on_delete=models.CASCADE, related_name="questions")
    student_text = models.TextField()
    reply = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    answered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["created_at"]


class Indicator(models.Model):
    """A new way students get a criterion wrong, noticed while marking.

    Attaches to the criterion, not to the marker and not to the student, so
    it survives seven of eight sessional tutors leaving.
    """

    criterion = models.ForeignKey(Criterion, on_delete=models.CASCADE, related_name="indicators")
    text = models.CharField(max_length=300)
    contributed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                       null=True, blank=True, related_name="indicators")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text


class HandoverNote(models.Model):
    """Attached to the assessment, not to the person who wrote it."""

    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name="handover_notes")
    text = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                               null=True, blank=True, related_name="handover_notes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class TutorialCoverage(models.Model):
    """A tutor marking a criterion as covered in their tutorial.

    The coordinator sees that it happened, not who taught what.
    """

    criterion = models.ForeignKey(Criterion, on_delete=models.CASCADE, related_name="coverage")
    tutorial_group = models.CharField(max_length=20)
    covered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("criterion", "tutorial_group")]
