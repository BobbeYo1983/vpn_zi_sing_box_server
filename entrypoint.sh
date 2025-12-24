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
python -c "from vpn.singbox import write_config; write_config()"

# -------------------------
# Запуск контейнера
# -------------------------
exec "$@"