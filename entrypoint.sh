#!/bin/sh
set -e

# -------------------------
# Подготовка базы данных
# -------------------------
echo "Making migrations ..."
python manage.py makemigrations vpn

echo "Applying database migrations..."
python manage.py migrate --noinput

# -------------------------
# Сбор статических файлов
# -------------------------
echo "Collect static files..."
python manage.py collectstatic --noinput

# -------------------------
# Запуск контейнера
# -------------------------
exec "$@"