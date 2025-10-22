# ===== Build stage =====
FROM python:3.11-slim AS build

WORKDIR /app

RUN apt-get update && apt-get install -y \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

COPY . .

ENV PYTHONPATH=/app



# ===== Runtime stage =====
FROM python:3.11-slim

WORKDIR /app

RUN useradd -m appuser

RUN apt-get update && apt-get install -y \
    netcat-openbsd \
    curl \
    && rm -rf /var/lib/apt/lists/*
COPY --from=build /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=build /usr/local/bin /usr/local/bin
COPY . .
RUN chmod +x entrypoint.sh

EXPOSE 8000
HEALTHCHECK CMD curl -f http://localhost:8000/health || exit 1

USER appuser

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["./entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
