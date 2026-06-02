FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry

COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && poetry install --without dev --no-root

COPY . .

RUN mkdir -p /app/static/tryon_results && chmod -R 777 /app/static/tryon_results

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]