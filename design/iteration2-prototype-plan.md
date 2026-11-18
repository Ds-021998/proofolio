# COMP7110 — Iteration 2 prototype plan (student side)

_Source: project doc `claude/iteration2-prototype-plan.md`. Teammate and tutor names replaced with roles._

Written 17 Sep 2026. Iteration 2 due **25 Sep** (8 days). Code + iteration 3 due 13 Nov.
Side committed: **student** (Loop 1). Basis: the clickable storyboard built by a teammate
(`feedback-action-clickable-storyboard.html`, 9 screens) + iteration 1 feedback from our tutor.

---

## 1. What the current prototype is, and what it isn't

Nine screens, all happy path, all canned content: login → home → upload → processing → 3 priority
issues → issue detail (where / why / what to do) → follow-up Q&A → later upload → comparison.

It is a good **communication** artefact. It is not yet an **experiment**, and iteration 2 grades the
experiment. Five problems to fix before it goes in front of anyone.

### 1.1 It contradicts our own problem statement

Our diagnosis was *feedback arrives too late to act on* — week 8 marks, assignment 2 started week 6.
But this app only starts working **after** feedback arrives. It makes late feedback more readable;
it does not make it timely. A marker will notice.

Two honest options — pick one and say it out loud in the canvas:

- **(a) Restate the problem.** The binding constraint we found isn't lateness, it's that feedback is
  unusable when it does arrive. Fine — but then H1 changed, and we must show the interview evidence
  that moved it.
- **(b) Keep the timing problem and move the mechanism.** The *comparison* screen — last
  assignment's issues surfaced against the new one — is the only part of this prototype that
  actually crosses the time gap. Right now it's screen 9 of 9, an afterthought. **It should be the
  centre of the product.**

Recommend (b). See §2.

### 1.2 The strongest idea is buried

> **The pre-submission check is the product. The post-feedback explainer is the on-ramp.**

An issue identified in assignment 1 becomes a checkable action that reappears **while you are
writing assignment 2**, before you submit — not after the next mark lands. That is the only design
in this prototype that closes Loop 1 in time, and it is also the answer to §1.3.

This is exactly the "cross-assessment memory" approach we listed under area B in the six-areas
research doc. We already named it; we just didn't build it.

### 1.3 No answer to ChatGPT

A student can paste their rubric and feedback into ChatGPT today, free, and get a competent
explanation. As built, our prototype is a worse ChatGPT with an upload form. Defensible wedges,
ranked:

1. **Persistence across assignments** — ChatGPT doesn't know what you were told last time. (§1.2)
2. **Anchoring** — quotes *your* paragraph and the *rubric's* wording, not a general essay tip.
3. **Integrity-safe by design** — it will not rewrite your work. ChatGPT will. (§1.4)
4. **Escalation** — a pre-written, specific question to send the tutor.

Test this directly in the sessions: *"What do you do today when feedback doesn't make sense?"* If
the answer is "ask ChatGPT" and they shrug at our four points, that's the finding, and it's more
valuable than a polished screen.

### 1.4 The "Improved" example is an adoption killer

The issue-detail screen shows the student's own sentence rewritten for them:

> Before: "Model A achieved higher accuracy."
> Improved: "Model A achieved higher accuracy, suggesting that feature X provides useful predictive
> information for this dataset."

That is ghostwriting their assignment. A course coordinator sees that screen and the product is
dead at UQ, regardless of how students react. Redesign:

- State the **criterion** ("an analysis sentence names the result *and* what it implies for your
  argument").
- Show a worked example from a **different** piece of work — a different topic, visibly not theirs.
- Never touch their submitted text.

Worth testing with a tutor as well as students — "would you be comfortable with your students using
this?" is a yes/no that decides the business model.

### 1.5 Nothing can go wrong in it

There is no screen for: the AI misread the feedback, the feedback was two vague lines, the student
disagrees, confidence is low. Our own research notes say tone is load-bearing and false confidence
harms. Add a **"this doesn't match my feedback"** control on every issue. It's good design, and it's
a free research instrument — every tap is recorded disagreement.

Minor: the login screen teaches us nothing. Cut it from the test build.

---

## 2. Proposed flow for iteration 2

| # | Screen | What it must prove |
|---|--------|--------------------|
| 1 | Home — two doors: **"I got feedback"** / **"I'm writing the next one"** | The second door is the differentiator. Watch which one they tap unprompted. |
| 2 | Add feedback — assignment + rubric + feedback, with a visible path for *"my feedback is two lines"* | Real inputs are thin. Don't hide it. |
| 3 | Priority issues — max 3, each showing where it came from | Do they believe it? |
| 4 | Issue detail — **where** (quote from their text) / **why** (rubric clause, verbatim) / **what to do** (criterion + external example) / **"this doesn't match"** | Comprehension + trust + integrity. |
| 5 | My actions — issues become a checklist that persists | Turns reading into a commitment. |
| 6 | **Pre-submission check** — before you hand in the next one, here are the 3 things you were told last time | The whole thesis of the product. |
| 7 | What changed — resolved / still present / new | Earned now, because a mechanism connects the two. |
| 8 | Ask my tutor — sends a specific pre-written question | Keeps Loop 2 alive for iteration 3. |

Every screen in that table maps to one testable assumption. Any screen that doesn't, we don't build
this week.

---

## 3. Build it at three fidelities — don't skip the first

### Fidelity 1 — Wizard of Oz (Thu–Fri, costs nothing, highest value)

The riskiest assumption is not "can we make screens" — it's **does real tutor feedback contain
enough signal to produce a useful where/why/what-to-do**. Test that without any code:

1. Collect **5 real, de-identified feedback comments** from our own past assignments.
2. By hand, write the where / why / what-to-do for each. An LLM may assist, but a human checks every
   line against the rubric.
3. Show each student the output for feedback they actually received, and ask: *is this right? Is
   this what the tutor meant? What would you have done with this?*

### Fidelity 2 — the clickable prototype (weekend)

Rebuild the storyboard on the §2 flow, using the Fidelity 1 content.

### Fidelity 3 — the executing app (start now, finish for 13 Nov)

Skeleton this week: repo, upload handling, one real LLM call, stored issues between two assignments.
It needs **commits every few days from now to November**.

---

## 4. Test plan for the sessions

- **Who:** 5 students who have received feedback on an assignment this semester, + 1 tutor (for
  §1.4). Not teammates. Not people who already know the idea.
- **Bring:** their own real feedback.
- **Format:** 30 min, task-based, no tour. *"Here's the app. Using this, tell me what you'd change
  in your next assignment."* Then stay quiet.
- **Measure:**
  - Can they restate the issue in their own words? (comprehension)
  - Time to naming one concrete thing they'd change. (value)
  - What do they do today instead? (competitor — expect ChatGPT)
  - Do they tap "this doesn't match"? On which issue? (trust)
  - Behavioural commitment: *"Can I message you the day before your next assignment is due?"*
- **Do not ask:** would you use this, would you pay, wouldn't it be great if.

Iteration 1 marked our experiment design as *not yet* — close-ended, rapid-fire, sometimes leading —
and interviews got attributed to the wrong members. So: one written script used by everyone, pauses
after answers, follow-ups instead of the next question, and **every interview logged under the name
of the person who actually ran it**, in the repo, at the time.

---

## 5. Week plan

| Day | Work |
|-----|------|
| Thu 17 | Agree the 3 riskiest assumptions. Write test cards **before** building. Split roles. Open one small GitHub issue per assumption. |
| Fri 18 | 5 WoZ samples written. Recruitment messages **sent**. |
| Sat–Sun 20–21 | Rebuild clickable prototype on §2 flow with real content. Code skeleton committed. |
| Mon 22 | Run 5 sessions. |
| Tue 23 | Synthesise → learning cards. Update the canvas: the value proposition must visibly move. |
| Wed 24 | Tidy BMC. Rehearse demo. |
| Thu 25 | Submit with buffer. |

---

## 6. Open items

- Which of §1.1 (a) or (b) the team picks.
- Whether the tutor-side escalation (screen 8) stays in scope for iteration 3 or is cut.
- Interview findings from iteration 1 live in the team repo.
