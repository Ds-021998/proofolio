# Accessibility — Proofolio

**Target: WCAG 2.1 Level AA.**

This is not a compliance exercise bolted on at the end. Proofolio is a product
whose whole claim is that a student can *see the standard they're being judged
against*. A student who can't read the screen can't see the standard.

What follows is what the template pack already does, and the checks to run
before the hand-in.

---

## 1. Built in already

### Structure

- Every page uses real landmarks: `<header>`, `<nav>`, `<main id="main">`,
  `<article>`, `<ol>`. A screen-reader user can jump between regions.
- `<h1>` is the wordmark on the login page; every inner page leads with `<h2>`
  in `.head` and uses `<h3>` for section kickers. Headings never skip a level.
- **A skip link is the first focusable element on every page** (`.skip` in
  `base.html`), visible on focus, jumping to `#main`.
- `<main>` carries `tabindex="-1"` so the skip link actually moves focus.
- Every page has a unique, descriptive `<title>` — WCAG 2.4.2.

### Status is never colour alone — WCAG 1.4.1

This is the one that catches most student projects, and the one Proofolio is
most exposed to, because the whole interface is a traffic light.

Every status chip carries **an icon and a word** as well as a colour:

| Verdict | Colour | Icon | Word |
|---|---|---|---|
| Met | emerald `#06795a` | tick | "Met" |
| Partly met | amber `#b5820c` | dot | "Partly met" |
| Not met | rose `#a1293c` | triangle | "Not met" |

Remove the colour entirely and the screen still reads correctly. Test it:
print a page in greyscale, or run the browser's monochrome emulation.

The capability meter has `role="img"` and an `aria-label` giving the number in
words, because the bar on its own means nothing to a screen reader. The number
above it is the real answer; the bar is decoration that happens to be
informative.

### Controls

- The verdict control is a **radio group inside a `<fieldset>`** with an
  `sr-only` `<legend>` naming the criterion. Arrow keys move between options,
  which is how a radio group is supposed to behave. It is not three buttons
  with `aria-pressed`, and it is not a `<div>` with a click handler.
- It posts with the surrounding form, so **marking works with JavaScript
  turned off.** No judgement in this product depends on a script running.
- Nav items are `<a href>`, not buttons: back button, bookmarking and
  open-in-new-tab all work.
- `aria-current="page"` marks the current nav item — not just a colour change.
- Every icon-only element is `aria-hidden="true"` with adjacent text, or
  carries an `sr-only` label. There are no bare icon buttons.
- Touch targets are at least 40px high (`.btn`), 34px for the segmented
  control, 32px for `.btn.xs`.

### Forms

- Every input has a real `<label for="...">`. No placeholder-as-label
  anywhere — a placeholder disappears the moment someone types.
- Help text is linked with `aria-describedby`, so it's announced with the
  field rather than orphaned after it.
- Errors are prefixed with the **word** "Error", coloured rose, and linked by
  `aria-describedby`; the field gets `aria-invalid="true"`.
- `autocomplete="username"` / `"current-password"` on the login form —
  WCAG 1.3.5.
- Forms use `novalidate` where we show our own messages, so a browser bubble
  doesn't compete with the one a screen reader will read.

### Feedback

- Django messages render in a `role="status"` `aria-live="polite"` list.
- Messages **do not auto-dismiss.** A toast that fades after three seconds is
  a timed interaction (WCAG 2.2.1) and it fails anyone who reads slowly.

### Motion and preferences

- `@media (prefers-reduced-motion: reduce)` kills every transition and
  animation.
- Light and dark are both first-class: tokens are redefined under
  `prefers-color-scheme: dark` and under an explicit `[data-theme]`.
- Nothing flashes, nothing autoplays, nothing moves on its own.

### Focus

- `:focus-visible` draws a 2px brand outline with 2px offset on everything
  focusable. **Do not add `outline: none` anywhere.** If a focus ring looks
  wrong, change its colour, never remove it.

---

## 2. Contrast

Measured, not estimated. Every pair below was computed with the WCAG 2.1
relative-luminance formula; the script is in `docs/contrast.py` so anyone can
re-run it after changing a token.

**Light theme**

| Pair | Ratio | Needs |
|---|---|---|
| `--ink` on `--surface` | 18.53:1 | 4.5:1 |
| `--ink-2` on `--surface` | 7.11:1 | 4.5:1 |
| `--ink-3` on `--surface` | 5.19:1 | 4.5:1 |
| `--ink-3` on `--surface-2` | 4.87:1 | 4.5:1 |
| `--ink-3` on `--ground` | 4.56:1 | 4.5:1 |
| `--brand` on `--surface` | 5.40:1 | 4.5:1 |
| `--ok` on `--ok-soft` (Met chip) | 4.64:1 | 4.5:1 |
| `--open` on `--open-soft` (Partly chip) | 4.54:1 | 4.5:1 |
| `--miss` on `--miss-soft` (Not met chip) | 6.10:1 | 4.5:1 |
| `--info` on `--info-soft` | 5.93:1 | 4.5:1 |
| white on `--brand` (primary button) | 5.40:1 | 4.5:1 |
| white on `--open` (Partly selected) | 5.11:1 | 4.5:1 |
| white on `--miss` (Not met selected) | 7.25:1 | 4.5:1 |

**Dark theme**

| Pair | Ratio |
|---|---|
| `--ink` on `--surface` | 15.31:1 |
| `--ink-2` on `--surface` | 7.94:1 |
| `--ink-3` on `--surface` | 4.64:1 |
| `--ok` on `--ok-soft` | 7.62:1 |
| `--open` on `--open-soft` | 9.43:1 |
| `--miss` on `--miss-soft` | 6.28:1 |
| `#06231a` on `--brand` (button) | 8.20:1 |

### Two colours were changed from the prototype

Measuring found two real failures in the tested prototype, and the stylesheet
fixes both. Worth saying in the write-up, because "we measured and found two
problems" is a stronger claim than "we designed it accessibly".

| Token | Was | Now | Why |
|---|---|---|---|
| `--ink-3` | `#7e8b85` | `#62706a` | 3.55:1 on white — failed for 12px metadata text |
| `--open` | `#b5820c` | `#8f6708` | 3.03:1 on `--open-soft` — the "Partly met" chip failed |

The darker amber also fixed the selected state of the verdict control: it
had near-black text on mid-amber at 3.37:1, and now carries white at 5.11:1,
the same treatment as the other two options.

**Rule for anyone adding a colour:** run `python3 docs/contrast.py` before you
commit it. Below 4.5:1 for body text, or 3:1 for a border or icon, pick a
different shade.

---

## 3. Responsive

- Single-column throughout. Nothing depends on a wide viewport.
- Works at **320px** with no horizontal scroll (WCAG 1.4.10).
- Works at **200% zoom** without loss of content or function (WCAG 1.4.4).
- The nav scrolls horizontally on narrow screens rather than wrapping into an
  unusable pile; it's a list of links, so scroll is the honest behaviour.
- Font sizes are in px but the layout is fluid; nothing is sized in `vw` in a
  way that breaks on zoom.

---

## 4. Before the hand-in — the checks to actually run

Half an hour, and it catches nearly everything.

1. **Keyboard only.** Unplug the mouse. Tab through login → dashboard →
   submit → marking → release → feedback → record. Everything reachable,
   focus always visible, nothing trapped, tab order matches reading order.
2. **320px.** Chrome DevTools, device toolbar, 320 × 640. No horizontal
   scrollbar on any page.
3. **200% zoom.** Ctrl/Cmd + until the page is at 200%. Nothing clipped,
   nothing overlapping.
4. **Greyscale.** DevTools → Rendering → Emulate vision deficiencies →
   Achromatopsia. Every status still readable.
5. **A screen reader, on two pages.** VoiceOver (Cmd+F5 on Mac) or NVDA
   (free, Windows) on the student dashboard and the tutor marking screen.
   You are listening for: the page title, the headings, the criterion titles,
   and the verdict group announcing which criterion it belongs to.
6. **Automated pass.** Run axe DevTools or Lighthouse on each of the eleven
   pages. Zero critical issues. Automated tools catch about a third of real
   problems, so this is the floor, not the ceiling.
7. **JavaScript off.** Mark a script and release it. It must work.

Record the results — date, what you ran, what you found, what you fixed — in
`docs/decisions.md`. Being able to say "we tested at 320px and at 200% zoom
with a screen reader, here's what we found" is worth more in the write-up than
any claim of compliance.

---

## 5. Known gaps, stated honestly

- **No screen-reader testing with an actual screen-reader user.** We tested
  with the software, not with someone who uses it daily. Those are different
  things and we shouldn't claim the second.
- `--ink-3` on `--ground` is 4.56:1 — above the line, but only just. It's used
  for secondary metadata, never for anything a user must read to act.
- Contrast is measured for text pairs. Non-text contrast (WCAG 1.4.11) for
  borders, the meter segments and the bar fills has been eyeballed, not
  measured.
- No testing with voice control (Dragon, Voice Control) or with a switch
  device.

Gaps named are better than gaps hidden. If a marker asks about accessibility,
this section is the answer that shows judgement.
