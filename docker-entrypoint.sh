#!/bin/sh
set -e

if [ "$1" = 'eddy-backend' ]; then
    python3 manage.py migrate
    python3 manage.py createadminuser
    exec uwsgi --ini uwsgi.ini
fi

exec "$@"
