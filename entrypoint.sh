#!/bin/sh
while ! nc -z db 5432; do
  sleep 1
done

alembic upgrade head

exec "$@"
