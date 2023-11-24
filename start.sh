cd /app

python app/pre_start.py

alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 80 --reload