# Running the Proofolio prototype locally

Proofolio lives in `apps/proofolio/`. It is a Django application with no build
step and no external services — Python and a browser are all it needs.

About ten minutes the first time.

---

## 1. Prerequisites

| Tool | Check it's there | If it isn't |
| --- | --- | --- |
| Python 3.12+ | `py --version` | python.org/downloads — tick **Add to PATH** during install |
| Git | `git --version` | `winget install --id Git.Git -e`, then restart your editor |

If `git --version` still fails after installing and restarting, Git is on the
machine but not on `PATH`. On Windows, run this once:

```powershell
[Environment]::SetEnvironmentVariable("Path", [Environment]::GetEnvironmentVariable("Path","User") + ";C:\Program Files\Git\cmd", "User")
```

Then close the editor completely and reopen it. Environment changes only reach
terminals opened afterwards.

---

## 2. Get the code

```powershell
git clone https://github.com/COMP1100-COMP7110-2026-s2/COMP7110-35_Srikrishna.git
cd COMP7110-35_Srikrishna
```

Cloning a private repository opens a browser window for GitHub sign-in. If a
different account is already signed in there, the clone fails with
`repository not found` rather than an authentication error.

---

## 3. Run it

The Django project is inside `apps/proofolio`, so start there:

```powershell
cd apps\proofolio
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py seed
python manage.py runserver
```

Then open **http://127.0.0.1:8000/**.

On macOS or Linux, replace the two Windows-specific lines:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

`127.0.0.1` means *this computer*. The server is only reachable from the
machine running it — the address cannot be shared with anyone else.

Stop the server with `Ctrl+C`. Each new terminal needs the virtual environment
activated again before `python manage.py ...` will work.

---

## 4. Signing in

The database is not in the repository, which is why `migrate` and `seed` are
needed. `seed` creates the course, its criteria, twelve students, a marker and
a coordinator, with one assessment already marked and released so there is
something to look at.

Three accounts cover the three roles. They are listed on the sign-in page
itself, and in `apps/proofolio/README.md`.

Each browser holds one session, so signing in as a second role signs the first
one out. To see two roles side by side, use a private window for the second.

---

## 5. How the project is laid out

| Path | What's in it |
| --- | --- |
| `proofolio/` | Django settings, root URL configuration, WSGI and ASGI entry points |
| `core/models.py` | The nine tables — courses, assessments, criteria, submissions, judgements |
| `core/views.py` | One function per page; all the application logic |
| `core/urls.py` | Which URL maps to which view |
| `core/decorators.py` | `@role_required` — the check that keeps roles apart |
| `core/forms.py` | Sign-up, including course join-code validation |
| `core/templates/` | Page templates, grouped by role, plus shared components in `includes/` |
| `static/css/` | `app.css` for the application, `landing.css` and `auth.css` for the public pages |
| `core/management/commands/seed.py` | Builds the demonstration data |

Deployment configuration is in `infra/deployment/`. Accessibility notes and the
template context reference are in `docs/engineering/`.

---

## 6. Troubleshooting

**`Activate.ps1 cannot be loaded` on Windows** — PowerShell blocks local
scripts by default:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

**`no such column` or another database error** — the database is out of step
with the models. Rebuild it:

```powershell
python manage.py migrate
python manage.py seed --reset
```

**The page loads but has no styling** — the virtual environment probably isn't
active. Activate it and run `pip install -r requirements.txt` again.

**`python` opens the Microsoft Store** — Windows has a stub where Python should
be. Use `py` instead of `python`, or reinstall Python with **Add to PATH**
ticked.

**Port 8000 already in use** — another server is still running. Either stop it,
or use a different port:

```powershell
python manage.py runserver 8001
```

**`ModuleNotFoundError: No module named 'django'`** — you're outside the
virtual environment. Activate it and try again.
