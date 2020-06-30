source venv/bin/activate
python -m pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
celery worker -A ImageResizer --concurrency=4 &>/dev/null &
redis-server &>/dev/null &
python manage.py runserver
