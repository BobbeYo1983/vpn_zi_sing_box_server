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

# Генерируем конфиг singbox при старте контейнера
python manage.py generate_singbox_config

# -------------------------
# Запуск контейнера
# -------------------------
exec "$@"