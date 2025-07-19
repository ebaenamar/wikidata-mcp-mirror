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

# Default to running the FastMCP server if no command is specified
if [ "$1" = 'server' ] || [ "$1" = 'gunicorn' ]; then
    echo "Starting Wikidata MCP Server with FastMCP SSE transport..."
    exec python server_sse.py
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
