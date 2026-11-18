# Start here

Four commands. Open `D:\MID\COMP7110` in VS Code, then open a terminal there
(**Terminal → New Terminal**, or `` Ctrl+` ``).

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed
python manage.py runserver
```

Then open **http://127.0.0.1:8000/** in a browser. You land on the public
page with **Log in** and **Sign up** buttons.

> **Renamed from Attested to Proofolio.** The Django project package is now
> `proofolio/`. **Delete the old `attested/` folder** if it is still there —
> two settings packages in one repo will confuse everyone, including you.
>
> Already ran this before? Run `python manage.py migrate` again, and note the
> demo password changed to `proofolio`.

> If `python` isn't found, try `py` instead — you have Anaconda installed, so
> `python` should work from a normal PowerShell window.
> If PowerShell refuses to run `activate`, run this once:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

## Signing up as a new student

Click **Sign up** and use the join code **`QILIN-7110`**.

Every account made this way is a **student**. There is no role picker,
deliberately: a judgement is the one thing only a marker can write, so letting
someone choose "tutor" at sign-up would undo the rule the product rests on.
Markers and coordinators are promoted by a coordinator in `/admin`.

## Three logins

| Username | Role | Password |
|---|---|---|
| `student1` | Student | `proofolio` |
| `tutor1` | Sessional marker | `proofolio` |
| `coord1` | Course coordinator | `proofolio` |

`coord1` is also a superuser, so **http://127.0.0.1:8000/admin/** works.

## The ninety-second demo

Two browser windows side by side — one normal, one incognito — so you can be
a student and a tutor at the same time.

1. **student1** → Home. *Two of five capabilities verified, three criteria
   still open from Assignment 1.*
2. **Assignment 2** → the three carried-in criteria are highlighted amber.
   Type a pointer in one ("section 2, paragraph 3"), paste any five lines of
   text, **Submit**.
3. **tutor1** → lands on the **Tutorial brief**. *Nobody wrote this. It's
   what the marking already said, counted.*
4. **Marking** → the script is waiting. The student's pointer is on screen.
   Judge all five. Notice the comment filling itself in, and that **there is
   no timer**. Add an indicator on one. **Release**.
5. **student1** → **Feedback**. *Closed by your marker · still open · newly
   open* — each criterion compared with the last time it was judged.
6. **Ask about this** → send a question. Back on **tutor1 → Questions**, the
   reply is already drafted from the standard the coordinator wrote. Send it.
7. **student1** → **My record** → **Preview what an employer sees**. Only
   closed capabilities travel, and the number that stayed behind is on screen.
8. **coord1** → **Handover**. The indicator the tutor typed sixty seconds ago
   is already there, attached to the criterion rather than to the tutor.

Closing line for step 8: *nothing extra was written by anyone — that handover
is a by-product of marking that already had to happen.*

## Putting it on a live URL

See **DEPLOY.md** — GitHub, then Render, about twenty minutes. The repo
already has `render.yaml` and `build.sh`, so there is no form to fill in.

## Resetting between demos

```powershell
python manage.py seed --reset
```

Note that `--reset` deletes and recreates the rows, so the ids in URLs change.
Click through the nav rather than reusing a bookmarked `/assessment/2/`.

## If something breaks

Copy the whole red traceback from the terminal and paste it to me. The last
line is the one that matters, but send all of it.
