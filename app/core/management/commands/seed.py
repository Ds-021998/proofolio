"""
Seed the database with a demo course.

    python manage.py seed          # create, skip anything that exists
    python manage.py seed --reset  # delete the demo data first, then create

Built as a management command rather than typed into /admin, because you will
reset the database more than once and you don't want to retype it.

What it creates
    12 students, 1 tutor, 1 coordinator — password "proofolio" for all
    student1 / tutor1 / coord1 are the three you demo with
    1 course, 2 assessments, 5 criteria
    Assignment 1, already marked and released — so the record has a history
      and Assignment 2 has something to carry forward

After running it, log in as student1 and the dashboard shows 2 of 5 verified
with three criteria carried in. That is the demo.
"""

import datetime

from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from core.models import (
    Assessment,
    Course,
    Criterion,
    Enrolment,
    Indicator,
    Judgement,
    Submission,
    Verdict,
)

PASSWORD = "proofolio"
GROUP = "T03"

CRITERIA = [
    dict(
        order=1,
        title="States the trade-off behind each design decision",
        capability_name="Design judgement",
        sfia_code="DESN 4",
        clause="For each design decision, name what it costs and who it costs.",
        good_looks_like="Each decision names the stakeholder it affects, not only the decision.",
        prefilled_comment="You describe the decision but not who it affects. Name the stakeholder "
                          "and what the decision costs them.",
        what_to_do="Name the stakeholder affected by each trade-off, not only the trade-off.",
        first=Verdict.PARTLY,
    ),
    dict(
        order=2,
        title="Evidence is traceable to a named source",
        capability_name="Research synthesis",
        sfia_code="RSCH 3",
        clause="Every claim about users points to something you collected or cited.",
        good_looks_like="A reader can follow any claim back to an interview, a dataset or a citation.",
        prefilled_comment="Several claims have no source behind them. Point each one at the interview "
                          "or the citation it came from.",
        what_to_do="Attach a source to every claim about what users do.",
        first=Verdict.NOT_MET,
    ),
    dict(
        order=3,
        title="Distinguishes a finding from an interpretation",
        capability_name="Analysis",
        sfia_code="",
        clause="Separate what participants said from what you concluded from it.",
        good_looks_like="The reader can tell which sentences are data and which are yours.",
        prefilled_comment="Your findings and your interpretations run together. Mark which is which.",
        what_to_do="Say what was observed, then say separately what you take it to mean.",
        first=Verdict.MET,
    ),
    dict(
        order=4,
        title="Scopes the recommendation to the evidence collected",
        capability_name="Scoping",
        sfia_code="BURM 4",
        clause="Keep the recommendation inside what your evidence can support.",
        good_looks_like="The recommendation is no wider than the sample behind it.",
        prefilled_comment="The recommendation is wider than the evidence behind it. Scope it to what "
                          "you actually collected.",
        what_to_do="Narrow the recommendation until the evidence covers it.",
        first=Verdict.MET,
    ),
    dict(
        order=5,
        title="Names what would change the conclusion",
        capability_name="Critical reasoning",
        sfia_code="",
        clause="State what evidence would overturn your conclusion.",
        good_looks_like="There is a sentence saying what you would need to see to be wrong.",
        prefilled_comment="Nothing here says what would change your mind. Add the evidence that "
                          "would overturn the conclusion.",
        what_to_do="Add one sentence naming what would overturn your conclusion.",
        first=Verdict.PARTLY,
    ),
]

A1_TEXT = """This report sets out the design decisions made during iteration one.
We chose a single-column layout because it was simpler to build and the team was short on time.
Students said they preferred the clearer labels.
On that basis the university should adopt this approach across all courses.
The design works and we are confident in it."""

# Variants, so the tutorial brief shows three different sentences rather than
# the same one three times. Each line is a different real-looking way to miss
# the matching criterion.
VARIANTS = [
    ["We went with option B after discussion.",
     "Users generally find this kind of thing confusing.",
     "Participants liked it, which shows the design is better.",
     "Every course should run assessments this way.",
     "We are sure this is the right approach."],
    ["The layout was chosen to save development time.",
     "Research shows students prefer simpler interfaces.",
     "People said it was clearer, so it is clearer.",
     "This should be rolled out faculty-wide next semester.",
     "Nothing in our testing contradicted the design."],
    ["A single column made the build easier for us.",
     "It is well known that students skim feedback.",
     "The feedback was positive so the concept is validated.",
     "We recommend adopting this across the program.",
     "We did not find any problems with the approach."],
    ["We picked the simpler option under time pressure.",
     "Students in general do not read rubrics.",
     "Three people liked it, so the design succeeds.",
     "All courses in the school should use this.",
     "The conclusion holds regardless of sample size."],
]


def body_for(index):
    """Build one student's Assignment 1 text from the variant pool."""
    v = VARIANTS[index % len(VARIANTS)]
    return "This report sets out the design decisions made during iteration one.\n" + "\n".join(v)


class Command(BaseCommand):
    help = "Create demo data for Proofolio."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Delete the demo data first.")

    @transaction.atomic
    def handle(self, *args, **options):
        if options["reset"]:
            Course.objects.filter(code="COMP7110").delete()
            User.objects.filter(username__startswith="student").delete()
            User.objects.filter(username__in=["tutor1", "coord1"]).delete()
            self.stdout.write("Deleted existing demo data.")

        # --- groups: this IS the permission model -----------------------
        groups = {}
        for name in ("student", "tutor", "coordinator"):
            groups[name], _ = Group.objects.get_or_create(name=name)

        # --- three users, one per role ----------------------------------
        people = {
            "student1": ("student", "Alex", "Nguyen"),
            "tutor1": ("tutor", "Sam", "Mahmoud"),
            "coord1": ("coordinator", "Chris", "Carter"),
        }
        users = {}
        for username, (role, first, last) in people.items():
            user, created = User.objects.get_or_create(
                username=username,
                defaults=dict(first_name=first, last_name=last, email=f"{username}@example.edu"),
            )
            if created:
                user.set_password(PASSWORD)
                user.save()
            user.groups.set([groups[role]])
            users[username] = user
        users["coord1"].is_staff = True
        users["coord1"].is_superuser = True
        users["coord1"].save()

        # --- course and enrolments --------------------------------------
        course, _ = Course.objects.get_or_create(
            code="COMP7110",
            defaults=dict(name="Introduction to Software Innovation", join_code="QILIN-7110"),
        )
        if not course.join_code:
            course.join_code = "QILIN-7110"
            course.save()
        for u in users.values():
            Enrolment.objects.get_or_create(user=u, course=course, defaults=dict(tutorial_group=GROUP))

        # --- two assessments: the record needs a trajectory --------------
        today = timezone.localdate()
        a1, _ = Assessment.objects.get_or_create(
            course=course, order=1,
            defaults=dict(title="Assignment 1", due_date=today - datetime.timedelta(days=42), is_published=True),
        )
        a2, _ = Assessment.objects.get_or_create(
            course=course, order=2,
            defaults=dict(title="Assignment 2", due_date=today + datetime.timedelta(days=11), is_published=True),
        )

        # --- the same five criteria on both assessments ------------------
        made = {}
        for spec in CRITERIA:
            for assessment in (a1, a2):
                c, _ = Criterion.objects.get_or_create(
                    assessment=assessment, order=spec["order"],
                    defaults=dict(
                        title=spec["title"],
                        capability_name=spec["capability_name"],
                        sfia_code=spec["sfia_code"],
                        clause=spec["clause"],
                        good_looks_like=spec["good_looks_like"],
                        prefilled_comment=spec["prefilled_comment"],
                        what_to_do=spec["what_to_do"],
                        is_published=True,
                    ),
                )
                made[(assessment.order, spec["order"])] = c

        # --- Assignment 1, marked and released ---------------------------
        sub1, created = Submission.objects.get_or_create(
            student=users["student1"], assessment=a1,
            defaults=dict(text=A1_TEXT, marking_seconds=31 * 60),
        )
        if created or not sub1.released_at:
            sub1.released_at = timezone.now() - datetime.timedelta(days=28)
            sub1.save()

        for spec in CRITERIA:
            criterion = made[(1, spec["order"])]
            Judgement.objects.get_or_create(
                submission=sub1, criterion=criterion,
                defaults=dict(
                    verdict=spec["first"],
                    comment="" if spec["first"] == Verdict.MET else spec["prefilled_comment"],
                    marker=users["tutor1"],
                ),
            )

        # --- a cohort, so the brief and the cohort view show real spread --
        # Eleven more students, same group, with varied Assignment 1 results.
        # Without them every bar reads 1/1 and the screens prove nothing.
        spread = [
            "mmpmp", "pnmmn", "mmmpn", "nmpmm", "mpmnp", "mmnpm",
            "pmmmn", "mnmpm", "mmpnp", "npmmm", "mmmnp",
        ]
        letter = {"m": Verdict.MET, "p": Verdict.PARTLY, "n": Verdict.NOT_MET}
        for i, pattern in enumerate(spread, start=2):
            username = f"student{i}"
            peer, created = User.objects.get_or_create(
                username=username,
                defaults=dict(first_name=f"Student", last_name=str(i),
                              email=f"{username}@example.edu"),
            )
            if created:
                peer.set_password(PASSWORD)
                peer.save()
            peer.groups.set([groups["student"]])
            Enrolment.objects.get_or_create(user=peer, course=course,
                                            defaults=dict(tutorial_group=GROUP))
            sub, made_sub = Submission.objects.get_or_create(
                student=peer, assessment=a1,
                defaults=dict(text=body_for(i), marking_seconds=29 * 60),
            )
            if made_sub or not sub.released_at:
                sub.released_at = timezone.now() - datetime.timedelta(days=28)
                sub.save()
            for spec, ch in zip(CRITERIA, pattern):
                verdict = letter[ch]
                Judgement.objects.get_or_create(
                    submission=sub, criterion=made[(1, spec["order"])],
                    defaults=dict(
                        verdict=verdict,
                        comment="" if verdict == Verdict.MET else spec["prefilled_comment"],
                        marker=users["tutor1"],
                    ),
                )

        # --- one indicator, so the handover screen isn't empty ------------
        Indicator.objects.get_or_create(
            criterion=made[(1, 2)],
            text="Students cite the assignment brief as if it were evidence.",
            defaults=dict(contributed_by=users["tutor1"]),
        )

        self.stdout.write(self.style.SUCCESS("\nSeeded COMP7110."))
        self.stdout.write(
            "\n  student1 / tutor1 / coord1    password: %s"
            "\n  student2..student12 fill out the cohort."
            "\n\n  Join code for signing up as a new student: QILIN-7110"
            "\n  coord1 is also a superuser, so /admin works."
            "\n\n  Assignment 1 is marked and released: 2 of 5 met."
            "\n  Three criteria carry into Assignment 2.\n" % PASSWORD
        )
