web: gunicorn crm_cryo.wsgi:application --bind 0.0.0.0:$PORT
worker: celery -A crm_cryo worker --loglevel=info
beat: celery -A crm_cryo beat --loglevel=info
