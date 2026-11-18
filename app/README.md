# Proofolio

**The criteria you were marked on, back when you need them.**

Thundering Qilins (Group 35) · COMP7110 Introduction to Software Innovation
Built by Dattatray Siraskar with a teammate (TZ)

A Django app that keeps the judgement a marker makes against a criterion,
instead of throwing it away when the mark is released. The same criterion the
coordinator already wrote is published to students before they write, clicked
by the marker instead of typed, used as the anchor for a follow-up question,
carried into the next assessment, and accumulated into a dated record of what
the student can do — proofolio by the teaching team rather than claimed by the
student.

**Running it: see [START-HERE.md](START-HERE.md).** Four commands.

---

## Accounts for assessment

All three use the password **`proofolio`**. They also appear on the sign-in
page itself, so nobody has to go looking.

| Username | Role | What it can do |
|---|---|---|
| `student1` | Student | Submit, read released feedback, ask a question, hold the capability record |
| `tutor1` | Sessional marker | Tutorial brief, mark a script, release, answer questions, own marking time |
| `coord1` | Course coordinator | Criteria, cohort view, handover — also a superuser, so `/admin` works |

New students can sign themselves up with the join code **`QILIN-7110`**.
Sign-up only ever creates a student; markers are promoted from inside the
course.

**Open a second role in a private window.** Signing in as the tutor in the
same browser signs the student out, and the loop needs both.

To hide the panel on the sign-in page, set `SHOW_DEMO_LOGINS=False` in the
environment.

## What works right now

The whole loop, end to end, with real logins and a real database.

| | |
|---|---|
| **Student** | sees published criteria before submitting · carried-in open criteria highlighted at the submission step · optional pointer per carried criterion · released feedback compared against the last judgement (*closed / still open / newly open*) · anchored question · capability record with a timeline · employer export preview |
| **Tutor** | tutorial brief counted from their own group's marking · marking queue · judge met/partly/not met with the comment pre-filled · contribute an indicator · release · answer questions from a pre-draft · own marking time, in aggregate |
| **Coordinator** | criteria list and editor · cohort view · handover: indicators and notes attached to the criterion |
| **Everyone** | Django auth, three Groups, `/admin` |

## How it's built

```
manage.py                     run everything through this
requirements.txt              Django, and nothing else
proofolio/settings.py          short on purpose — every line is explainable
core/
  models.py                   9 tables
  views.py                    every view, with the access rules at the top
  decorators.py               @role_required — the access control, 30 lines
  context_processors.py       role, role_label, course, home_url on every page
  admin.py                    every model registered
  urls.py                     every URL name
  management/commands/seed.py demo data: 3 users, 2 assessments, 5 criteria
  templates/                  30 files: a base, 11 components, 18 pages
static/css/app.css            the design system, ported from the prototype
docs/                         context contract · accessibility · contrast checker
```

### The one rule

> A `Judgement` is only ever created by a user in the **tutor** or
> **coordinator** group. A student can never create or edit one.

Everything else follows. Every view is `@login_required`; each one filters its
queryset by the signed-in user, so a student's page never queries anything but
their own rows. A criterion is **open** if its most recent judgement is not
`met` — one rule, and it powers the carry-forward, the record and the meter.

### Where the design came from

`app.css` is the stylesheet from `proofolio-prototype-v2.html`, the version
participants actually clicked through in iteration 2. No downloaded template.
Every screen traces to feedback we received:

| Feedback | What the app does |
|---|---|
| "Students self-ticking *applied* is not acceptable" | Self-certification removed. A criterion closes only when a marker next judges it met, and the screen says so. The student can leave a *pointer*, never a verdict. |
| "The marking timer looks like surveillance" | No timer renders while marking. Time accrues server-side and appears only in that tutor's own aggregate view. |
| "What's a checkpoint that a rubric isn't?" | The word is gone. These are the coordinator's existing rubric criteria, used at four moments instead of one. |
| "Who sets them — coordinator or tutor?" | Coordinator owns the criteria; tutors contribute *indicators* as a by-product of marking. |
| "Tutors already help students in tutorials" | The tutorial brief feeds the tutorial instead of competing with it. |
| Role switching confused usability participants | One account, one role. There is no control anywhere that switches roles. |

---

## Verified

Clicked through end to end with Playwright against a running server, as all
three roles:

| Check | Result |
|---|---|
| Full loop: submit → mark → release → feedback → ask → answer → record → export → handover | passes, no 5xx |
| Student reaching `/marking/`, `/marking/1/`, `/criteria/` | 403 |
| Tutor reaching `/record/` | 403 |
| Signed out reaching `/home/` | redirected to login |
| Unknown ids: `/assessment/999/`, `/ask/999/` | 404, not 403 |
| axe-core, WCAG 2.0/2.1 A + AA, all 18 pages | 0 violations |
| Contrast, 21 colour pairs, light and dark | all pass, minimum 4.54:1 |
| 320px viewport and 200% zoom | no horizontal overflow |
| Keyboard, marking screen | skip link first, visible 2px focus ring, each verdict group one tab stop |

Two colours were changed from the prototype because measuring found real
failures: `--ink-3` was 3.55:1 and the amber "Partly met" chip was 3.03:1.
Run `python docs/contrast.py` before adding any colour.

Still to do before the hand-in: a screen reader on two pages, a greyscale
check, and marking a script with JavaScript disabled (it should work — the
verdict control is a radio group inside the form, not a script).

---

## Who did what

| Dattatray (me) | Teammate (TZ) |
|---|---|
| Templates, CSS, copy for every screen | Models and migrations |
| Student views | Tutor and coordinator views |
| Seed data, docs, demo script | Access control tests, deployment |

Commit small and often with real messages — individual contribution is graded
from the repository log.

## Not building, ever

- Anything that produces text a student could submit
- A leaderboard or public ranking on assessment performance
- A label on a student's own submitted work
- Automated grading, re-grading or grade prediction
