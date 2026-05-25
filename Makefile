# Переменные
DOCKER_COMPOSE = docker-compose -f infra/docker-compose.yml
BACKEND_CONTAINER = backend

.PHONY: help up down restart logs migrate load-data shell clean

help:
	@echo "Доступные команды:"
	@echo "  make up          - собрать и запустить проект, применить миграции, загрузить данные"
	@echo "  make down        - остановить контейнеры"
	@echo "  make restart     - перезапустить контейнеры"
	@echo "  make logs        - посмотреть логи"
	@echo "  make migrate     - вручную применить миграции"
	@echo "  make load-data   - вручную загрузить начальные данные"
	@echo "  make shell       - зайти в shell контейнера backend"
	@echo "  make clean       - остановить контейнеры и удалить volumes (потеряете БД)"

# Проверка наличия .env файла, создание из примера
.env:
	@if [ ! -f .env ]; then \
		echo "Файл .env не найден. Создаю из .env.example"; \
		cp .env.example .env; \
	fi

# Запуск контейнеров
docker-up: .env
	$(DOCKER_COMPOSE) up -d --build

# Применение миграций БД
migrate:
	@echo "Применяю миграции Alembic..."
	$(DOCKER_COMPOSE) exec $(BACKEND_CONTAINER) alembic upgrade head

# Загрузка начальных данных (если есть скрипт)
load-data:
	@echo "Загружаю начальные данные..."
	@if $(DOCKER_COMPOSE) exec -T $(BACKEND_CONTAINER) python -c "import app.initial_data" &>/dev/null; then \
		$(DOCKER_COMPOSE) exec -T $(BACKEND_CONTAINER) python -m app.initial_data; \
	else \
		echo "Скрипт начальных данных не найден (app/initial_data.py). Пропускаю."; \
	fi

# Главная команда: поднять проект с данными
up: docker-up migrate load-data
	@echo "✅ Проект запущен! Доступен по адресу http://localhost:8000"

# Остановка контейнеров
down:
	$(DOCKER_COMPOSE) down

# Перезапуск
restart: down up

# Логи
logs:
	$(DOCKER_COMPOSE) logs -f

# Shell в контейнере бэкенда
shell:
	$(DOCKER_COMPOSE) exec $(BACKEND_CONTAINER) bash

# Полная очистка (удаление volumes)
clean:
	$(DOCKER_COMPOSE) down -v