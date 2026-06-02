DOCKER_COMPOSE = docker-compose -f infra/docker-compose.yml
BACKEND_CONTAINER = backend
WORKER_CONTAINER = worker

.PHONY: help up down restart logs migrate load-data shell clean worker-logs beat-logs celery-status

help:
	@echo "Доступные команды:"
	@echo "  make up           - собрать и запустить проект, применить миграции, загрузить данные"
	@echo "  make down         - остановить контейнеры"
	@echo "  make restart      - перезапустить контейнеры"
	@echo "  make logs         - посмотреть все логи"
	@echo "  make worker-logs  - посмотреть логи Celery worker"
	@echo "  make beat-logs    - посмотреть логи Celery beat"
	@echo "  make migrate      - вручную применить миграции"
	@echo "  make load-data    - вручную загрузить начальные данные"
	@echo "  make shell        - зайти в shell контейнера backend"
	@echo "  make clean        - остановить контейнеры и удалить volumes"
	@echo "  make celery-status- проверить статус Celery задач"

.env:
	@if [ ! -f .env ]; then \
		echo "Файл .env не найден. Создаю из .env.example"; \
		cp .env.example .env; \
	fi

docker-up: .env
	$(DOCKER_COMPOSE) up -d --build

migrate:
	@echo "Применяю миграции Alembic..."
	$(DOCKER_COMPOSE) exec $(BACKEND_CONTAINER) alembic upgrade head

load-data:
	@echo "Загружаю начальные данные..."
	@if $(DOCKER_COMPOSE) exec -T $(BACKEND_CONTAINER) python -c "import app.initial_data" &>/dev/null; then \
		$(DOCKER_COMPOSE) exec -T $(BACKEND_CONTAINER) python -m app.initial_data; \
	else \
		echo "Скрипт начальных данных не найден. Пропускаю."; \
	fi

up: docker-up migrate load-data
	@echo "Проект запущен! Доступен по адресу http://localhost"

down:
	$(DOCKER_COMPOSE) down

restart: down up

logs:
	$(DOCKER_COMPOSE) logs -f

worker-logs:
	$(DOCKER_COMPOSE) logs -f worker

beat-logs:
	$(DOCKER_COMPOSE) logs -f celery-beat

celery-status:
	$(DOCKER_COMPOSE) exec $(WORKER_CONTAINER) celery -A worker.celery_app inspect active
	$(DOCKER_COMPOSE) exec $(WORKER_CONTAINER) celery -A worker.celery_app inspect scheduled

shell:
	$(DOCKER_COMPOSE) exec $(BACKEND_CONTAINER) bash

clean:
	$(DOCKER_COMPOSE) down -v
