release: python scripts/setup_database.py && python scripts/update_daily.py
web: gunicorn run:app
clock: python clock.py