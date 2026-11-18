# Attested / Proofolio — coded MVP (iteration 3)

_Source: project doc `claude/mvp-template-pack.md`, written 22 Oct 2026._

> **Source code:** `proofolio-app/` in this folder — 68 files copied from my laptop on 17 Nov 2026
> (no `.venv`, database or caches). Two team-distribution scripts and a team setup note were left out
> because they name teammates; teammate names in the README and comments are replaced with roles.
> Re-checked on 17 Nov: `manage.py check` passes, migrations and seed run, and every page loads for
> all three roles. The app was renamed from "Attested" to "Proofolio" in Nov 2026, and the demo
> password is `proofolio` (seeded demo accounts only).

## Running it

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed
python manage.py runserver
```

Demo logins: `student1` / `tutor1` / `coord1` (seeded demo accounts). `python manage.py seed --reset`
between demos. Full demo script in `START-HERE.md`.

## Deploying

`DEPLOY.md`: push to GitHub → Render **New → Blueprint** (`render.yaml` + `build.sh`). Handled up
front: WhiteNoise static files under `DEBUG=False`; `SECRET_KEY` from env; `CSRF_TRUSTED_ORIGINS`
from `RENDER_EXTERNAL_HOSTNAME`; `SECURE_PROXY_SSL_HEADER`; SQLite on a mounted disk via `DB_DIR`.

## What works — the whole loop, end to end, with real logins and a real database

- **Student** — published criteria before submitting; carried-in open criteria highlighted at
  submission; pointer per carried criterion; feedback compared against the last judgement (closed /
  still open / newly open); anchored question; capability record with timeline; employer preview.
- **Tutor** — tutorial brief from their own group's marking; marking queue; met/partly/not met with
  pre-filled comment; indicators; release; answer questions from a pre-draft; own marking time.
- **Coordinator** — criteria list and editor; cohort view; handover attached to the criterion.

## Stack and shape

Django 5+/SQLite, Django templates, no JS framework, no API layer. Gunicorn + WhiteNoise.

```
attested/settings.py                env-driven for Render
core/models.py                      9 tables
core/views.py                       every view, access rules stated at the top
core/decorators.py                  @role_required (~30 lines)
core/context_processors.py          role, role_label, course, home_url
core/management/commands/seed.py    12 students, 2 assessments, 5 criteria
core/templates/                     30 files: base, 11 components, 18 pages
static/css/app.css                  ported from the v2 prototype
docs/                               template-context.md, accessibility.md, contrast.py
render.yaml, build.sh               Render blueprint
```

**The one rule:** a `Judgement` is only created by a tutor or coordinator. A criterion is **open** if
its most recent judgement is not `met` — that single query powers the carry-forward, the record and
the meter.

## Verified (Playwright, all three roles, dev and production mode)

| Check | Result |
|---|---|
| submit → mark → release → feedback → ask → answer → record → export → handover | passes, no 5xx |
| same loop over HTTPS with `DEBUG=False` | passes; CSS served, CSRF OK |
| `manage.py check --deploy` | only the deliberate HSTS warning |
| student → tutor/coordinator URLs | 403 |
| tutor → `/record/` | 403 |
| signed out → `/home/` | redirect to login |
| another student's object | 404, not 403 |
| axe-core WCAG 2.0/2.1 A+AA, 18 pages | 0 violations |
| contrast, 21 pairs, light and dark | all pass, min 4.54:1 |
| 320px and 200% zoom | no horizontal overflow |
| keyboard, marking screen | skip link, 2px focus ring, one tab stop per verdict group |

### Bugs found by testing, and fixed

1. Release button stayed disabled until Save (no-JS form) — now the POST saves then counts; partial release refused with a message.
2. Attestation line missing the course code (context processor read a non-existent field).
3. Seed made one student, so bars read 1/1 — now 12 students with varied results.
4. Two palette colours failed AA (3.55:1 and 3.03:1) — darkened to pass.

## Design decisions to defend

CSS is the prototype's own · verdicts are a radio fieldset (works with JS off) · no marking timer on
screen · nothing on the student's feedback page can be ticked · another student's URL returns 404 ·
attestations name the teaching team, never the individual marker · HSTS deliberately off.

## Next steps recorded at the time (22 Oct)

Push to GitHub and add the second coder · deploy before 13 Nov · screen-reader, greyscale and no-JS
checks · still no coordinator interview.
