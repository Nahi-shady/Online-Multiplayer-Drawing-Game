release: cd backend && pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
web: cd backend && daphne -b 0.0.0.0 -p $PORT illustra_backend.asgi:application
