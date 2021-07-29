release: python manage.py migrate
web: gunicorn SaleRecord.wsgi  --preload --timeout 300 