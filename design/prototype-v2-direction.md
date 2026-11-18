# COMP7110 — Prototype v2: direction (the pivot to an attested capability record)

_Source: project doc `claude/prototype-v2-direction.md`, 24 Sep 2026. Responds to tutor + course coordinator feedback on prototype v1._

## Part 1 — The objections that decide the project

### 1.1 "What is a checkpoint that a rubric isn't?"

Concede the artefact and claim the moments:

> We are not introducing a new artefact. We take the rubric criterion you already wrote and make it
> present at four moments where it currently isn't: while the student writes, while the tutor marks,
> when the student asks about the result, and in the next assessment.

Consequence: drop the word "checkpoint" from the UI. Call them criteria.

### 1.2 "Who sets them — coordinator or tutor?"

| | Owns | Why them | Frequency |
|---|---|---|---|
| **Coordinator** | The criteria and standards | Accountable for the course profile, here next year | Once per assessment |
| **Tutor** | The observable indicators — what the failure looks like on a page | Only they read 60 scripts | Added while marking, as a by-product |
| **Neither** | The verdict on a given script | That is marking. It stays where it is. | Per script |

### 1.3 "Tutors already help students in weekly tutorials"

Reposition: **we feed the tutorial, we don't replace it.** Before a tutorial the tutor sees which
criterion most of their group missed, with three de-identified paragraphs, and a ten-minute opener.

## Part 2 — Point-by-point fixes to v1

| Feedback | Fix in v2 |
|---|---|
| Role switching confused usability participants | A **launcher** chooses the mode before the session. No in-session role switch. |
| Carry-forward "will students even check?" | Attach it to the **submission gate** and the **tutorial brief**. Never a notification. |
| Student self-ticking "applied" not acceptable | Removed. An open criterion closes **only at the next marking event**. |
| What is the research layer for? | Moved out of the build into a facilitator sheet. |
| Marking timer feels like surveillance | Hidden. Shown only to that tutor, in aggregate, after the fact. |

## Part 3 — The v2 thesis

> **AI made formative feedback abundant. It made attested evidence of ability scarce.**
> Don't compete with AI on explaining feedback. Build the thing AI structurally cannot produce: a
> qualified person's dated, evidenced observation of what this student actually did.

**The product: an attested capability record.** Each criterion carries a capability name (course
learning outcomes; draft SFIA mapping). Each marking event becomes a dated, attested observation.
Across a degree: "in March this person could not link evidence to a claim, by October they could —
here is the marked work and here is who verified it".

## Part 4 — Build scope (iteration 3)

1. Launcher with three modes.
2. Coordinator view: criteria per assessment, each tagged with a capability name.
3. Tutor: mark against criteria; add an indicator as a by-product; timer hidden.
4. **Tutorial brief** — new headline feature.
5. Student: submission gate with open criteria; anchored question; feedback view; no self-ticking.
6. Student capability record, read-only, with the marked work behind each observation.

Defer / cut: live model call to generate criteria; job board; cross-course dashboard; employer export (design only).

## Part 5 — Decisions taken, 24 Sep

1. **The capability record is the product.** The unit changes from the assignment to the
   criterion-over-time; the demo must span two assessments; the record must be honest (no
   self-certification).
2. **Four roles, not one buyer:** student = user; course coordinator = champion; sessional tutor =
   gatekeeper; school/faculty = buyer. *Pitch the coordinator, design for the student.*
3. **Employer value is a stated assumption.** McKay & Watty (Deakin, 2016) — 14 Australian
   employers saw value in ePortfolios but objected that they are time-consuming, template-like and
   hard to verify; all three come from self-curation, which this design removes. Still an
   assumption → test card, not a finding.
   **My hypothesis, recorded verbatim in the plan:** employers want a *progressive* candidate, not a
   CV listing skills and courses with no evidence of what was learned from them.

## Part 6 — Still open

Privacy of an attested record of weaknesses · gaming pressure on markers · cold start across courses.
