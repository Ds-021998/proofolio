"""
Django settings for Proofolio.

Kept deliberately short. Every line here is one you should be able to
explain — if a setting isn't needed, it isn't in the file.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# On your laptop these fall back to development values and you set nothing.
# On Render, SECRET_KEY and DEBUG come from the environment, so the real
# secret is never in the repository.
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-not-a-secret")
DEBUG = os.environ.get("DEBUG", "True") == "True"

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
RENDER_HOST = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if RENDER_HOST:
    ALLOWED_HOSTS.append(RENDER_HOST)
    # Django 4+ checks the Origin header on POSTs over HTTPS. Without this,
    # every form on the deployed site fails CSRF validation.
    CSRF_TRUSTED_ORIGINS = [f"https://{RENDER_HOST}"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # Serves static files in production. Django's dev server does it for you
    # when DEBUG is True; nothing does it when DEBUG is False, which is why
    # a deployed Django site so often appears with no CSS.
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "proofolio.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "core" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # Supplies role, role_label, course and home_url on every page.
                "core.context_processors.proofolio",
            ],
        },
    },
]

WSGI_APPLICATION = "proofolio.wsgi.application"

# On your laptop the database sits next to manage.py. On Render it has to
# live on the mounted disk (see render.yaml): Render wipes the filesystem on
# every deploy, so a SQLite file anywhere else would be erased each push and
# every login with it.
DB_DIR = Path(os.environ.get("DB_DIR", BASE_DIR))
DB_DIR.mkdir(parents=True, exist_ok=True)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": DB_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-au"
TIME_ZONE = "Australia/Brisbane"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"       # where collectstatic puts them

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Authentication. Django ships the login view, the password hasher and the
# session cookie — we write none of that.
# Shows the three assessment accounts on the sign-in page. Handy while this
# is being marked; set SHOW_DEMO_LOGINS=False in the environment to hide them.
SHOW_DEMO_LOGINS = os.environ.get("SHOW_DEMO_LOGINS", "True") == "True"

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "post_login"
LOGOUT_REDIRECT_URL = "login"

# Only when deployed. Render terminates HTTPS at its proxy and passes the
# original scheme in a header, which is what SECURE_PROXY_SSL_HEADER reads —
# without it Django thinks every request is plain HTTP and redirects forever.
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    # HSTS is deliberately left off. It tells browsers to refuse plain HTTP
    # for this domain for a fixed period, and it cannot be undone quickly.
    # Not something to switch on for a course project on a free subdomain.
