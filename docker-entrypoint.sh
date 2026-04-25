#!/bin/sh
set -e
export PORT="${PORT:-80}"

envsubst '$PORT' < /etc/nginx/templates/default.conf.template > /etc/nginx/sites-enabled/default

runuser -u app -- uvicorn main:app --host 127.0.0.1 --port 8080 &

exec nginx -g "daemon off;"
