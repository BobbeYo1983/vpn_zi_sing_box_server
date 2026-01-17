.PHONY: build migrate static up down deploy logs clean

# Цвета для вывода
YELLOW := \033[1;33m
NC := \033[0m # No Color

build:
	@echo "$(YELLOW)=== Building vpn_zi_sing_box_server ===$(NC)"
	docker compose build vpn_zi_sing_box_server

migrate:
	@echo "$(YELLOW)=== Running migrations ===$(NC)"
	docker compose run --rm vpn_zi_sing_box_server python manage.py migrate --noinput

static:
	@echo "$(YELLOW)=== Cleaning staticfiles ===$(NC)"
	rm -rf data/staticfiles/*
	@echo "$(YELLOW)=== Fix permissions ===$(NC)"
	sudo chown -R 1000:1000 data/ || true
	@echo "$(YELLOW)=== Collecting static files ===$(NC)"
	docker compose run --rm vpn_zi_sing_box_server python manage.py collectstatic --noinput --clear

up:
	@echo "$(YELLOW)=== Starting services ===$(NC)"
	docker compose up -d

down:
	@echo "$(YELLOW)=== Stopping services ===$(NC)"
	docker compose down

deploy: build migrate static up
	@echo "$(YELLOW)=== DEPLOYMENT COMPLETE ===$(NC)"

logs:
	docker-compose logs -f vpn_zi_sing_box_server

clean:
	@echo "$(YELLOW)=== Cleaning ===$(NC)"
	docker compose down -v
	docker system prune -f

help:
	@echo "Available commands:"
	@echo "  make build     - Build vpn_zi_sing_box_server image"
	@echo "  make migrate   - Run database migrations"
	@echo "  make static    - Collect static files"
	@echo "  make up        - Start services"
	@echo "  make deploy    - Full deploy (build+migrate+static+up)"
	@echo "  make down      - Stop services"
	@echo "  make logs      - Show logs"
	@echo "  make clean     - Full cleanup"