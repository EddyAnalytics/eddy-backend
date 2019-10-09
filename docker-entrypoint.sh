#!/bin/sh
set -e

if [ "$1" = 'eddy-backend' ]; then
  if [ $DB_TYPE = 'mysql' ]; then
    until mysql --host=$MYSQL_HOST --port=$MYSQL_PORT --user=$MYSQL_USER --password=$MYSQL_PASSWORD --execute="SHOW DATABASES;" $DB_NAME; do
      sleep 1
    done
    python3 manage.py collectstatic --no-input
    python3 manage.py makemigrations
    python3 manage.py migrate
    python3 manage.py createadminuser
    python3 manage.py createdebeziumintegrationtype
    python3 manage.py createdebeziumdataconnectortype
    exec uwsgi --ini uwsgi.ini
  else
    python3 manage.py collectstatic --no-input
    python3 manage.py makemigrations
    python3 manage.py migrate
    python3 manage.py createadminuser
    python3 manage.py createdebeziumintegrationtype
    python3 manage.py createdebeziumdataconnectortype
    exec uwsgi --ini uwsgi.ini
  fi
fi

exec "$@"
