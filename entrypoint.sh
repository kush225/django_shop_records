#!/bin/sh

echo "---------------------------------"
echo "making migrations..."
python manage.py makemigrations
echo "migrations are ready to be deployed"
echo "---------------------------------"
echo "deploying DB changes..."
python manage.py migrate
echo "creating Django super user..."
python manage.py initadmin
echo "Collecting Static file..."
echo "---------------------------------"
python manage.py collectstatic --noinput
echo "starting server"
#gunicorn -b 0.0.0.0:8000 infinity.wsgi
python manage.py runserver 0.0.0.0:8000

exec "$@"