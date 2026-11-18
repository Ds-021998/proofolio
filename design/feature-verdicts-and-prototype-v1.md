# COMP7110 — Feature verdicts and the built prototype (v1)

_Source: project doc `claude/feature-verdicts-and-prototype.md`, 17 Sep 2026._
_Working prototype: `../04-prototype/prototype-v1-feedback-to-action.html`._

---

## 1. The requirements, graded

| # | Requirement | Verdict | Why |
|---|---|---|---|
| 1 | Tutor uploads brief → app extracts assessable factors | **Excellent** | Created once per assignment, reused across 42 scripts. The only idea on the list whose cost does not scale with cohort size. |
| 2 | Tutor sets checkpoints; marking judged against them | **Excellent** | Same object, second use. Turns a blank comment box into three taps. |
| 3 | Tutor explains feedback fast without re-reading the script | **Excellent** | The checkpoint is the shared context, so a reply needs no re-reading. |
| 4 | **Checkpoints hidden from students** | **Worst on the list** | Inverts the feedback literature, likely breaches UQ's published-criteria requirement, and institutionalises the guesswork that is our stated problem. Cut. |
| 5 | Student sees what skills the assessment builds | **Good, if narrowed** | Vacuous if the skills are LLM-generated adjectives. Real if they are the rubric criteria, tracked cumulatively. |
| 6 | Cross-course skills dashboard | **Good, oversold** | Only as good as the courses that opt in. Show the cold start honestly. |
| 7 | Live chat tutor ↔ student | **Half good, half fatal** | The goal is right; "live" is what kills it. A casual tutor paid per script cannot accept unbounded synchronous time. |
| 8 | Class help guide / technical help forum | **Cut** | Ed Discussion is deployed at UQ and owns this. |
| 9 | Achievements + leaderboard | **Second worst** | Public ranking on assessment demotivates exactly the students who don't act on feedback — our target user. |
| 10 | Market-skills newsletter | **Cut** | A different product, for a different person, solving SDG 4.4. |

### The unifying finding

Requirements 1, 2, 3, 5, 6 are not five features. They are **five views of one object: the
checkpoint.**

> A checkpoint is written once by the tutor from the brief and the rubric. It is **published to
> students** as the standard before they start. It is what the **marker clicks** instead of typing.
> It is what a **student question is anchored to**, so the tutor can answer without reopening the
> script. It **carries into the next assignment** as an open item. It **aggregates across the
> cohort** into causes the coordinator can act on, and into a handover note that outlives the
> sessional tutor.

### Corrections applied

- **Hidden checkpoints → published standards, private judgements.**
- **Live chat → asynchronous, checkpoint-anchored, one-tap.**
- **Skills dashboard → criterion recurrence, private.** No rank, no cohort comparison.
- **Leaderboard → nothing.**
- **The app never judges.** The tutor judges; the app carries the judgement.

---

## 2. What is in the prototype

Two roles, one shared state — switching roles mid-demo is the point.

**Tutor:** draft checkpoints from the brief → edit them → publish → mark a script against them with
a visible timer → cohort view of which checkpoints the cohort failed, plus a handover note for next
semester → question queue with pre-drafted replies.

**Student:** dashboard of criteria still open from Assignment 1 → the published standards before
submitting, with last time's failures highlighted → a structure self-check that explicitly does not
rewrite your work → feedback anchored to a paragraph, with "this doesn't match my work" and "mark as
applied" → what changed since Assignment 1 → private criterion recurrence.

A **research layer** toggle shows, per screen, the assumption that screen tests and what to watch in
a session, plus jump-to-state controls. **Turn it off before testing with a participant.**

### Two-minute demo script

Student dashboard → switch to Tutor → draft checkpoints from brief → publish → switch to Student →
standards now visible, submit → switch to Tutor → mark five checkpoints (watch the timer) → release
→ switch to Student → feedback with resolved / still present / new → "Ask about this" → switch to
Tutor → answer in one tap → switch to Student → answer is there.

### Known gaps

- Checkpoint drafting from the brief is scripted, not a live model call.
- Cohort numbers are illustrative.
- **Nobody has interviewed a course coordinator**, and the cohort screen is aimed at one.
- Two-sided adoption is unproven.
