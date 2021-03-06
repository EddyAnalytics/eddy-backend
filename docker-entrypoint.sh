#!/bin/sh
set -e

until mysql --host=$MYSQL_HOST --port=$MYSQL_PORT --user=$MYSQL_USER --password=$MYSQL_PASSWORD --execute="SHOW DATABASES;" $DB_NAME; do
  sleep 1
done

if [ "$1" = 'eddy-backend-dev' ]; then
  python3 manage.py migrate --no-input
  python3 manage.py collectstatic --no-input
  exec uwsgi --ini uwsgi.dev.ini
  exec "$@"
elif [ "$1" = 'eddy-backend' ]; then
  python3 manage.py migrate --no-input
  python3 manage.py collectstatic --no-input
  exec uwsgi --ini uwsgi.ini
  exec "$@"
fi
