#!/bin/sh
set -e

echo "Applying database migrations ..."
python manage.py migrate --noinput

echo "Collect static files ..."
python manage.py collectstatic --noinput

echo "Generate singbox config ..."
python manage.py generate_singbox_config

exec "$@"