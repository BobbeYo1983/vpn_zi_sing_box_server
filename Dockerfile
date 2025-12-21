# при выборе версии образа учитывать какую версию Django поддерживает.
# версия Django в requirements/requirements_docker_dev.txt
FROM python:3.13.7-alpine3.21

# Запрещает создавать .pyc файлы в контейнере
ENV PYTHONDONTWRITEBYTECODE=1

# Отключает буферизацию логов, чтобы показывать их сразу
ENV PYTHONUNBUFFERED=1

# Обновляем pip до последней версии
RUN python -m pip install --upgrade pip

WORKDIR /app

COPY /app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY ./app/ .

# Копируем подготовительный скрипт перед запуском приложения
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "core.wsgi:application", "-b", "0.0.0.0:8001", "--workers", "3"]