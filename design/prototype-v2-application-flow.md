# Attested — prototype v2, full application flow

_Source: project doc `claude/prototype-v2-flow.md`, 24 Sep 2026. Describes `../04-prototype/prototype-v2-attested.html`._

## 0. The one object everything hangs off

A **criterion** is the coordinator's existing rubric criterion, tagged with a capability name. It is
not a new artefact — it is the same criterion used at four moments instead of one.

```
  coordinator publishes it
            ↓
       [ PUBLISHED ]  ── student sees it before writing
            ↓
   marker judges the script
            ↓
   ┌── met ────────→ [ CLOSED ]  → becomes a verified, dated attestation
   ├── partly ─────→ [ OPEN ]    → carried into the next assessment
   └── not met ────→ [ OPEN ]    → carried into the next assessment
            ↓
   next assessment: judged again → may close, may stay open, may reopen
```

**Only a marker moves a criterion between states.** The student can never close one, and the app
never judges.

## 1. Entry — the launcher

| Choice | Opens | Used for |
|---|---|---|
| Student | Student app only | Usability session with a student |
| Tutor | Tutor app only | Session with a sessional marker |
| Coordinator | Coordinator app only | Session with the course coordinator |
| Side by side | Student **and** tutor, sharing one state | The pitch and the demo |

## 2. The semester loop

1. **Coordinator — Criteria.** Five criteria for Assignment 2, each mapped to a capability
   (Requirements definition · SFIA REQM, Research and experiment design · RSCH, Evidence-based
   analysis, Decision traceability, Business modelling · BSMO — SFIA marked "draft mapping"). All
   published to students.
2. **Student — Home.** Opens on the record: *2 of 5 capabilities verified*, next assessment, criteria
   still open from Assignment 1 ("closes when a marker next judges it met. You can't close it
   yourself.").
3. **Student — Assignment 2 (submission gate).** Carried-in criteria highlighted; optional *pointer*
   ("section 2, paragraph 3") — a pointer, not a claim.
4. **Tutor — Thursday brief.** From the previous marking, filtered to the tutor's own 20 students:
   three most-missed criteria, three de-identified sentences, a ten-minute opener, *Mark as covered*.
5. **Submission** fills the tutor's marking queue.
6. **Tutor — Marking.** Numbered paragraphs; one card per criterion; **Met / Partly / Not met**;
   pre-written comment attaches itself; optional one-line *indicator*. No visible timer. Release
   disabled until all five are judged.
7. **Student — Feedback.** Per criterion: *Closed by your marker* / *Still open* / *Newly open*, with
   where, what the marker wrote, next time, and *Ask about this*. Nothing can be ticked done.
8. **Asking.** Question arrives bound to the criterion and paragraph with a reply pre-drafted from the
   coordinator's standard. The script is never reopened.
9. **Student — My record.** Timeline per capability; verified seal; *Preview what an employer sees*
   — closed capabilities only, with trajectory ("Not met 12 Aug → met 24 Sep").
10. **Tutor — My time.** Hours vs paid allocation (e.g. 9.3 h vs 7 h); only that tutor sees it.
11. **Coordinator — Cohort and Handover.** Proportion bars across a cohort of 42; indicators
    attached to the criterion, so they survive tutor turnover.

## 3. What each event writes, and who sees it

| Event | Writes | Visible to |
|---|---|---|
| Coordinator publishes criteria | criteria + capability tags | students, markers |
| Student leaves a pointer | a location string | that script's marker |
| Marker judges a criterion | verdict + comment | the student, at release |
| Marker adds an indicator | a line against the criterion | coordinator handover, next semester |
| Criterion judged met | a dated attestation | the student's record; exportable |
| Criterion partly / not met | an open item | next submission gate; cohort view |
| Student asks a question | question bound to a criterion | marker's queue, with a pre-draft |
| Tutor marks brief covered | a covered flag | coordinator's cohort view |
| Marking time | seconds | that tutor only, in aggregate |

## 4. Demo script — about ninety seconds

1. Launcher → **Side by side**.
2. Tutor panel opens on **Thursday brief**.
3. Student → **Assignment 2** — three carried-in criteria. Type a pointer. **Submit.**
4. Tutor: judge five criteria, add one indicator, **Release.**
5. Student: two closed, one still open, one newly open.
6. Student → **Ask about this** → tutor answers from the pre-draft.
7. Student → **My record** → **Preview what an employer sees**.
8. Change role → **Coordinator** → **Handover**: the indicator typed a minute ago is already there.

## 5. What is simulated

Criteria pre-written (no live model); cohort numbers illustrative; export is a preview panel; SFIA mapping is a draft.
