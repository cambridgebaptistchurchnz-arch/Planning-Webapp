"""
Django settings for the church_roster project.

Configured to run locally with sane defaults, and on Render using
environment variables. See README.md for the full deploy walkthrough.
"""

import os
from pathlib import Path

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------
# Core / security
# ---------------------------------------------------------------------

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-insecure-key-change-me")

DEBUG = os.environ.get("DEBUG", "True") == "True"

ALLOWED_HOSTS = []

render_external_hostname = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if render_external_hostname:
    ALLOWED_HOSTS.append(render_external_hostname)

extra_hosts = os.environ.get("ALLOWED_HOSTS", "")
if extra_hosts:
    ALLOWED_HOSTS.extend([h.strip() for h in extra_hosts.split(",") if h.strip()])

if DEBUG:
    ALLOWED_HOSTS.extend(["localhost", "127.0.0.1"])

CSRF_TRUSTED_ORIGINS = []
if render_external_hostname:
    CSRF_TRUSTED_ORIGINS.append(f"https://{render_external_hostname}")

# ---------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "scheduling",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "roster.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "roster.wsgi.application"

# ---------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------
# Locally: falls back to SQLite if DATABASE_URL isn't set.
# On Render: set DATABASE_URL to the Postgres instance's Internal URL.

DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}

# ---------------------------------------------------------------------
# Passwords
# ---------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------

LANGUAGE_CODE = "en-us"
TIME_ZONE = os.environ.get("TIME_ZONE", "Pacific/Auckland")
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------
# Static files (whitenoise serves these directly from the Django app,
# no separate static file host needed)
# ---------------------------------------------------------------------

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------
# Works with any SMTP provider: Resend, SendGrid, Mailgun, Gmail app
# password, etc. During local dev with no EMAIL_HOST set, emails just
# print to the console instead of actually sending.

if os.environ.get("EMAIL_HOST"):
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = os.environ.get("EMAIL_HOST")
    EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
    EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
    EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True") == "True"
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "roster@example.org")

# Public base URL used to build the links volunteers click in emails.
# e.g. https://church-roster.onrender.com
SITE_URL = os.environ.get("SITE_URL", "http://127.0.0.1:8000")
