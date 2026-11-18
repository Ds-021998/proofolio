#!/usr/bin/env bash
# Render runs this on every deploy. Three steps, in this order.
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input   # copy CSS into staticfiles/
python manage.py migrate                    # create or update the tables
python manage.py seed                       # demo data; safe to re-run
