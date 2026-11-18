# Template context contract

What every view has to put in the context for its template to render. This is
the handover line between the two halves of the build: templates and CSS on one
side, models and views on the other.

Nothing here needs a custom template tag or filter. Where a template would have
had to compute something — a percentage, a count, whether a criterion carried
in — the **view** computes it and passes it in. Django templates deliberately
can't do arithmetic, and working around that is how template packs turn into
mud.

---

## Everywhere (from `core.context_processors.proofolio`)

| Name | Type | Notes |
|---|---|---|
| `role` | `"student"` / `"tutor"` / `"coordinator"` | read from Django Groups |
| `role_label` | str | "Student", "Sessional marker", "Course coordinator" |
| `course` | `Course` | needs `.code`, `.name` |
| `home_url` | str | where "Go home" goes for this role |

The nav also reads, where they exist:

| Name | Used by | Notes |
|---|---|---|
| `nav` | all | short string naming the current page — see each page below |
| `current_assessment_id` | student nav | int |
| `current_assessment_title` | student nav | str |
| `to_mark` | tutor nav | int, shows a badge |
| `open_q` | tutor nav | int, shows a badge |

---

## `student/dashboard.html` · `nav="home"`

| Name | Type |
|---|---|
| `verified_count`, `total_count` | int |
| `meter_segments` | list of `"ok"` / `"open"`, one per criterion, in order |
| `next_assessment` | object with `.id`, `.title`, `.due_date` |
| `open_criteria` | list of `Criterion`, each annotated `.verdict`, `.open_since`, `.what_to_do` |
| `tutorial_note` | str or None |
| `courses` | optional list with `.code`, `.name`, `.is_live`, `.verified` |
| `term_label`, `week_label` | optional str |

**A criterion is open if its most recent `Judgement` is not `met`.** One query,
and it powers this page, the carry-forward and the record.

```python
latest = (Judgement.objects
          .filter(submission__student=request.user, criterion=c)
          .order_by("-created_at").first())
is_open = latest is None or latest.verdict != "met"
```

---

## `student/assessment.html` · `nav="submit"`

| Name | Type |
|---|---|
| `assessment` | `.id`, `.title`, `.due_date` |
| `criteria` | list, each with `.id`, `.title`, `.capability_name`, `.sfia_code`, `.clause`, `.good_looks_like`, plus annotated `.carried_in` (bool) and `.pointer` (str) |
| `submission` | the student's `Submission`, or `None` |
| `feedback_ready` | bool |
| `feedback_url` | str, when `feedback_ready` |

POSTs `pointer-<criterion.id>` per carried criterion, plus `text`.
The pointer is stored on the `Submission`; it is **never** a verdict.

---

## `student/feedback.html` · `nav="feedback"`

| Name | Type |
|---|---|
| `assessment`, `released_at` | |
| `closed_count` | int |
| `results` | list, each with `.id`, `.title`, `.capability_name`, `.sfia_code`, `.verdict`, `.change`, `.quote`, `.para_number`, `.comment`, `.what_to_do`, `.verified_on` |
| `my_questions` | list with `.criterion_title`, `.text`, `.reply`, `.answered_at` |

`.change` is one of `"closed"`, `"still_open"`, `"newly_open"`, `""`, computed
in the view by comparing this judgement against the previous one on the same
criterion. That comparison is the demo.

---

## `student/record.html` · `nav="record"`

| Name | Type |
|---|---|
| `capabilities` | list, each `.name`, `.criterion_title`, `.sfia_code`, `.latest_verdict`, `.events` |
| `events` (inside each) | ordered oldest→newest, each `.assessment_title`, `.verdict`, `.created_at`, `.verified_by` |
| `closed_count`, `open_count` | int |

---

## `tutor/brief.html` · `nav="brief"`

| Name | Type |
|---|---|
| `group_size`, `tutorial_date` | |
| `bars` | list of `.label`, `.value`, `.total`, `.percent` (int, pre-computed), `.sub` |
| `top` | `.id`, `.title`, `.capability_name`, `.examples` (list of de-identified strings), `.opener`, `.covered` |

---

## `tutor/queue.html` · `nav="mark"`

| Name | Type |
|---|---|
| `assessment` | |
| `waiting` | list with `.id`, `.position`, `.submitted_at` |
| `done_count` | int |

**Filter to this tutor's assigned group.** A submission from another group
raises `Http404`, not `PermissionDenied`.

---

## `tutor/marking.html` · `nav="mark"`

| Name | Type |
|---|---|
| `submission` | `.id`, `.position`, `.cohort_size`, `.text_paragraphs` — a list of `{text, flagged}` |
| `criteria` | each `.id`, `.title`, `.capability_name`, `.para_label`, plus annotated `.verdict`, `.comment`, `.indicator`, `.pointer` |
| `judged_count` | int |
| `can_release` | bool |

POSTs `verdict-<id>`, `comment-<id>`, `indicator-<id>`, and `action` =
`save` or `release`.

`.comment` is pre-filled from `Criterion.prefilled_comment` the first time.
That pre-fill is the time saving, and it is why the handover note and the
cohort view cost nobody any extra typing.

**No timer renders on this page.** Accrue time server-side on the submission
and surface it only in `tutor/time.html`.

---

## `tutor/questions.html` · `nav="questions"`

| Name | Type |
|---|---|
| `waiting` | `.id`, `.criterion_title`, `.student_label`, `.text`, `.draft_reply` |
| `answered` | `.criterion_title`, `.student_label`, `.text`, `.reply`, `.answered_at` |

`.draft_reply` comes from the criterion's `good_looks_like` /
`prefilled_comment` — the standard the coordinator already wrote.

---

## `tutor/time.html` · `nav="time"`

| Name | Type |
|---|---|
| `hours_marked`, `paid_hours`, `difference` | str or Decimal, formatted in the view |
| `scripts_marked`, `average_minutes` | int |
| `over_allocation` | bool |

---

## `coordinator/criteria.html` · `nav="criteria"`

| Name | Type |
|---|---|
| `assessment` | |
| `criteria` | each with the Criterion fields plus `.is_published` and `.indicators` (list of `.text`) |
| `sfia_draft` | bool — shows the "drafts, not accredited" line |

## `coordinator/cohort.html` · `nav="cohort"`

| Name | Type |
|---|---|
| `cohort_size`, `weeks_remaining` | int |
| `bars` | as in the tutorial brief |
| `covered` | list of criterion titles |

## `coordinator/handover.html` · `nav="handover"`

| Name | Type |
|---|---|
| `criteria_with_indicators` | each `.title`, `.capability_name`, `.indicators` |
| `notes` | each `.text`, `.created_at` |

---

## Verdict values

Use these exact strings everywhere — model choices, template comparisons, POST
values. The CSS selectors key off them.

```python
class Verdict(models.TextChoices):
    MET = "met", "Met"
    PARTLY = "partly", "Partly met"
    NOT_MET = "not_met", "Not met"
```

| Verdict | Chip class | Meaning |
|---|---|---|
| `met` | `ok` (emerald) | closes the criterion; becomes a dated attestation |
| `partly` | `open` (amber) | stays open, carries into the next assessment |
| `not_met` | `miss` (rose) | stays open, carries into the next assessment |

---

## Percentages

Templates can't divide. Pass `percent` as an int:

```python
percent = round(100 * missed / total) if total else 0
```
