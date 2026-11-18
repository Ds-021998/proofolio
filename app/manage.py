#!/usr/bin/env python
"""Django's command-line utility. Run everything through this file:

    python manage.py migrate
    python manage.py seed
    python manage.py runserver
"""
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "proofolio.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Django isn't installed, or the virtual environment isn't active. "
            "Try: pip install -r requirements.txt"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
