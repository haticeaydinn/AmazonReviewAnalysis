web: gunicorn swe.wsgi --timeout 4800 --keep-alive 5 --log-file -
worker: python manage.py qcluster