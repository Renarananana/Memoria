#!/bin/sh

echo "🌍 Entorno: $ENV"

if [ "$ENV" = "prod" ]; then
  echo "🚀 Iniciando Gunicorn en producción..."
  python manage.py collectstatic --noinput
  gunicorn tu_proyecto.wsgi:application --bind 0.0.0.0:8000
else
  echo "🛠 Iniciando Django en modo desarrollo..."
  python manage.py migrate
  python manage.py runserver 0.0.0.0:8000
fi
