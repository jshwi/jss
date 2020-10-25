#!/usr/bin/env bash
#=======================================================================
#
#          FILE: release.sh
#
#         USAGE:  To be called by Dockerfile upon docker-compose build
#
#   DESCRIPTION:  Docker entry point
#                 Listen for PostgreSQL connection then execute command
#
#        AUTHOR:  Stephen Whitlock (jshwi), stephen@jshwisolutions.com
#       CREATED:  22/09/21 16:15:44
#      REVISION:  0.1.0
#=======================================================================
set -o errexit
set -o nounset

echo "Waiting for postgres..."
while ! nc -z "$SQL_HOST" "$SQL_PORT"; do
  sleep 0.1
done

echo "PostgreSQL started"
if [ "$FLASK_ENV" = "production" ]; then
  ./.venv/bin/pipenv run flask db upgrade
else
  ./.venv/bin/pipenv run flask create db
fi

exec "$@"
