#!/usr/bin/env bash
source .venv/bin/activate
python3 -m gunicorn.app.wsgiapp --bind 127.0.0.1:5000 --workers=3 wsgi:app server:app
