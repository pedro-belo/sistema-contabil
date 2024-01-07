#!/bin/bash

python manage.py migrate
python -m gunicorn -b 0.0.0.0:8000 equibook.wsgi --access-logfile /app/access.log --error-logfile /app/errors.log --capture-output
