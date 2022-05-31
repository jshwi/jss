release: chmod u+x scripts/release.sh && ./scripts/release.sh
web: gunicorn wsgi:app
worker: rq worker -u $REDIS_URL jss-tasks
