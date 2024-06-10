#!/bin/sh

python manage.py migrate
python -m gunicorn -b 127.0.0.1:8001 equibook.wsgi --access-logfile /app/access.log --error-logfile /app/errors.log --capture-output
