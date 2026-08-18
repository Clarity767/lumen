#!/usr/bin/env bash
set -o errexit
pip install -r requirements.txt
python manage.py findstatic restaurant/css/base.css --verbosity 3
python manage.py collectstatic --no-input
python manage.py migrate