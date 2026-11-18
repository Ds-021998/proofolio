# Putting Proofolio on a live URL

Twenty minutes, free tier, no card. Do it this week while nothing depends on
it — the build plan names last-day deployment as the top risk, and it is the
one that actually kills course projects.

The repo already contains everything Render needs: `build.sh`, `render.yaml`,
and `requirements.txt`.

---

## 1. Get the code on GitHub

In the VS Code terminal, in `D:\MID\COMP7110`:

```powershell
git init
git add .
git commit -m "Proofolio: Django MVP — models, auth, three roles, full loop"
git branch -M main
```

Then create an **empty** repo at github.com/new called `proofolio` — no README,
no .gitignore, we already have both — and:

```powershell
git remote add origin https://github.com/<your-username>/proofolio.git
git push -u origin main
```

Add your teammate as a collaborator in **Settings → Collaborators**.

> Individual contribution is graded from the repository log, so from here on:
> commit small and often, with messages that say what changed. Ten commits
> saying `add student feedback view` beat one saying `update`.

## 2. Connect Render

1. Sign in at **render.com** with GitHub.
2. **New → Blueprint**, pick the `proofolio` repo.
3. Render reads `render.yaml` and fills everything in. Click **Apply**.
4. First build takes 3–5 minutes.

You get a URL like `https://proofolio.onrender.com`. The same three logins
work — `student1`, `tutor1`, `coord1`, password `proofolio` — because
`build.sh` runs the seed.

## 3. Check it

- The page has styling. If it's unstyled white, `collectstatic` failed —
  check the build log.
- Log in as `student1`. If sign-in bounces back to the login page, the CSRF
  origin is wrong: confirm `RENDER_EXTERNAL_HOSTNAME` is set under
  **Environment** (Render sets it automatically).
- Submit something as a student, mark it as the tutor. A form that fails here
  but works locally is almost always CSRF.

---

## What's already handled

| Problem | Where it's solved |
|---|---|
| No CSS once `DEBUG=False` | WhiteNoise middleware + `CompressedManifestStaticFilesStorage` |
| Secret key in the repo | `SECRET_KEY` comes from the environment; Render generates it |
| CSRF failures on every form | `CSRF_TRUSTED_ORIGINS` built from `RENDER_EXTERNAL_HOSTNAME` |
| Infinite HTTPS redirect loop | `SECURE_PROXY_SSL_HEADER` — Render terminates TLS at its proxy |
| Database wiped on every deploy | SQLite lives on a mounted disk; `DB_DIR` points at it |

Tested here by running the app exactly as Render will: `DEBUG=False`,
`collectstatic`, gunicorn over real HTTPS. Login, submit and release all pass,
and `manage.py check --deploy` reports only the HSTS warning, which is
deliberate (see `settings.py`).

## Free tier, honestly

The service sleeps after 15 minutes idle and takes ~50 seconds to wake. Open
the URL a minute before you demo, or the room watches a spinner. It is not a
reason to pay — it is a reason to click the link early.

## Before anyone outside the team sees it

The seeded accounts all share the password `proofolio`, which is fine for a
course demo and not fine for anything else. If the coordinator is going to
use it with real work:

```powershell
python manage.py changepassword coord1
```

and delete the seeded students.
