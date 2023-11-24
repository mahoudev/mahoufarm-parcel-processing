cd /app

python app/pre_start.py

celery -A app.worker worker -l info
