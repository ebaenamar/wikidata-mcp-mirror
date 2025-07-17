#!/bin/bash
set -e

# Set default values
: ${WORKERS:=4}
: ${TIMEOUT:=120}
: ${KEEPALIVE:=5}
: ${PORT:=8000}

# Change to the source directory
cd /app

# If command starts with an option, prepend gunicorn
if [ "${1:0:1}" = '-' ]; then
    set -- gunicorn "$@"
fi

# Default to running gunicorn if no command is specified
if [ "$1" = 'gunicorn' ]; then
    exec gunicorn \
        --bind "0.0.0.0:${PORT}" \
        --workers "${WORKERS}" \
        --timeout "${TIMEOUT}" \
        --keep-alive "${KEEPALIVE}" \
        --worker-class uvicorn.workers.UvicornWorker \
        wikidata_mcp.api:app
else
    # Execute any other command
    exec "$@"
fi

# Wait for any services to be available (e.g., Redis, etc.)
# Example:
# while ! nc -z redis 6379; do
#   echo "Waiting for Redis..."
#   sleep 1
# done

# Run database migrations if needed
# Example:
# python manage.py migrate

# Start the server
exec "$@"
