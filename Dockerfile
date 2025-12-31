# при выборе версии образа учитывать какую версию Django поддерживает.
# версия Django в requirements/requirements_docker_dev.txt
FROM python:3.13.7-alpine3.21

# Запрещает создавать .pyc файлы в контейнере
ENV PYTHONDONTWRITEBYTECODE=1

# Отключает буферизацию логов, чтобы показывать их сразу
ENV PYTHONUNBUFFERED=1

# Обновляем pip до последней версии
RUN python -m pip install --upgrade pip

# Устанавливаем рабочую директорию внутри контейнера. Все последующие команды COPY, RUN, CMD будут выполняться относительно /app.
WORKDIR /app

# Установка зависимостей
COPY /app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Копируем приложение в корень контейнера
COPY ./app/ .

# Копируем подготовительный скрипт перед запуском приложения
COPY ./entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Скрипт перед запуском приложения
ENTRYPOINT ["/app/entrypoint.sh"]

# Команда запуска
CMD ["gunicorn", "core.wsgi:application", "-b", "0.0.0.0:8000", "--workers", "3"]