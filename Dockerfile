ARG USER=jss
# =============================== Base =================================
FROM python:3.8-alpine AS base

ARG USER
ARG WORKDIR=/home/$USER

# reduce image size and send output straight to terminal
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# add user to run container under and install `libpq` for `psycopg2` and
# `libstdc++` for multiple `Flask` extensions
RUN adduser --disabled-password $USER && apk add --no-cache libpq libstdc++

# set new user's $HOME as WORKDIR
WORKDIR $WORKDIR

# =========================== Poetry Base ==============================
FROM base AS poetry-base

# create virtualenv in workdir and execute `poetry` from ~/.local/bin
ENV POETRY_VIRTUALENVS_IN_PROJECT 1
ENV POETRY_HOME $WORKDIR/.local

# install dependencies for building `poetry` and other Python packages
# and build and install `poetry`
RUN apk add --no-cache curl g++ libffi-dev musl-dev && \
    curl -sSL https://install.python-poetry.org | python3 -

# ========================== Backend Builder ============================
FROM poetry-base AS backend-builder

# copy over files needed for installing Python packages with `poetry`
COPY ./pyproject.toml ./poetry.lock ./

# install dependencies for building `cryptography` and `psycopg2` and
# create virtualenv to copy into other images
RUN apk add --no-cache cargo postgresql-dev && \
    ./.local/bin/poetry install --no-dev --no-root --no-ansi

# ======================= Dev Backend Builder ==========================
FROM backend-builder AS dev-backend-builder

# install dev packages to virtualenv to copy into development image
RUN ./.local/bin/poetry install --no-root --no-ansi

# ========================= Frontend Builder ===========================
FROM node:18 AS frontend-builder

# copy over files needed to compile static assets
COPY ./webpack.config.js ./package.json ./package-lock.json ./
COPY ./assets ./assets

# compile static assets
RUN npm install && npm run webpack:prod

# ============================ Production ==============================
FROM base AS production

ENV FLASK_ENV production

# copy over app, database migrations, and wsgi entry point
COPY ./app ./app
COPY ./migrations ./migrations
COPY ./wsgi.py ./

# copy over prepared virtualenv from builder
COPY --from=backend-builder $WORKDIR/.venv ./.venv

# copy over prepared static assets from builder
COPY --from=frontend-builder ./app/static ./app/static

# run static digest on static assets, make sure static files are
# readable by `nginx`, then  pass ownership of all files to user
RUN ./.venv/bin/flask digest compile && \
    chmod 777 -R ./app/static && \
    chown -R $USER:$USER ./

# get out of root and run container as user
USER $USER

# run the application server
CMD ["./.venv/bin/gunicorn", "--bind=0.0.0.0:5000", "wsgi:app"]

# =========================== Development ==============================
FROM base AS development

ARG DEV_SECRET=dev
ARG DEV_EMAIL=admin@localhost

ENV FLASK_ENV development
ENV ADMINS $DEV_EMAIL
ENV ADMIN_SECRET $DEV_SECRET
ENV CSP_REPORT_ONLY 1
ENV DEBUG_TB_ENABLED 0
ENV DEFAULT_MAIL_SENDER $DEV_EMAIL
ENV LOG_LEVEL DEBUG
ENV NAVBAR_HOME 0
ENV NAVBAR_ICONS 1
ENV NAVBAR_USER_DROPDOWN 1
ENV SECRET_KEY $DEV_SECRET
ENV SEND_FILE_MAX_AGE_DEFAULT 0

# execute command defined in docker-compose.yml within this script
COPY ./bin/entrypoint ./

# copy over prepared python virtualenv from builder
COPY --from=dev-backend-builder $WORKDIR/.venv ./.venv

# install `netcat` to listen for `postgresql` container and pass
# ownership of all files to user
RUN apk add --no-cache netcat-openbsd && chown -R $USER:$USER ./

# get out of root and run container as user
USER $USER

# entry point to ensure database os running, upgrade database, and
# create admin, before starting dev server
ENTRYPOINT ["./entrypoint"]

# ============================== Nginx =================================
FROM nginx:1.21.4-alpine AS nginx

# remove default config in `nginx` container
RUN rm /etc/nginx/conf.d/default.conf

# copy over prepared config
COPY ./nginx.conf /etc/nginx/conf.d

# copy over certs for serving https requests locally
COPY ./certs /etc/nginx/ssl
