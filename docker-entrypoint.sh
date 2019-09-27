#!/bin/sh
set -e

if [ "$1" = 'eddy-backend' ]; then
    if [ $DB_TYPE = 'sqlite' ]; then
        python3 manage.py collectstatic
        python3 manage.py migrate
        python3 manage.py createadminuser
        exec uwsgi --ini uwsgi.ini
    else
        until mysql $MYSQL_HOST:$MYSQL_PORT -u $MYSQL_USER -p $MYSQL_PASSWORD exec \"SHOW DATABASES\"; do
          echo 'sleep'
          sleep 1
        done
        python3 manage.py collectstatic
        python3 manage.py migrate
        python3 manage.py createadminuser
        exec uwsgi --ini uwsgi.ini
    fi
fi

exec "$@"
