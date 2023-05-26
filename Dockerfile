# =============================== Base =================================
FROM python:3.11-alpine AS base

ARG USER=jss
ARG WORKDIR=/home/$USER
ARG VENV=$WORKDIR/.venv

# reduce image size, send output straight to terminal, and add
# virtualenv to PATH (venv needs to be in PATH for any scripts run
# outside of this context that aren't prefixed with $VENV/bin/)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PATH $VENV/bin:$PATH

# add user to run container under and install `libpq` for `psycopg2` and
# `libstdc++` for multiple `Flask` extensions
RUN adduser --disabled-password $USER && apk add --no-cache libpq libstdc++

# set new user's $HOME as WORKDIR
WORKDIR $WORKDIR

FROM base as dev-base

# install `netcat` to listen for `postgresql` container
RUN apk add --no-cache netcat-openbsd

# ======================= Backend Builder Base =========================
FROM base AS backend-builder-base

# create virtualenv in workdir, install `poetry` in $POETRY_HOME/bin/,
# and add $POETRY_HOME/bin to PATH
ENV POETRY_VIRTUALENVS_IN_PROJECT 1
ENV POETRY_HOME $WORKDIR/.local
ENV PATH $POETRY_HOME/bin:$PATH
ENV PIP_DEFAULT_TIMEOUT 100
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PIP_NO_CACHE_DIR 1
ENV POETRY_VERSION 1.1.13

# install dependencies for building `poetry`, and other Python packages
# (`cryptography` and `psycopg2` etc.), then build and install `poetry`
RUN apk add --no-cache \
    curl \
    cargo \
    g++ \
    libffi-dev \
    musl-dev \
    postgresql-dev && \
    curl -sSL https://install.python-poetry.org | python3 -

# ========================== Backend Builder ============================
FROM backend-builder-base AS backend-builder

# copy over files needed for installing Python packages with `poetry`
COPY ./pyproject.toml ./poetry.lock ./

# create virtualenv to copy into other images
RUN poetry install --no-dev --no-root --no-ansi

# ======================= Dev Backend Builder ==========================
FROM backend-builder AS dev-backend-builder

# install dev packages to virtualenv to copy into development image
RUN poetry install --no-root --no-ansi

# ========================= Frontend Builder ===========================
FROM node:20 AS frontend-builder

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
COPY ./wsgi.py ./bin/post_compile ./

# copy over prepared virtualenv from builder
COPY --from=backend-builder $VENV ./.venv

# copy over prepared static assets from builder
COPY --from=frontend-builder ./app/static ./app/static

# run static digest on static assets, make sure static files are
# readable by `nginx`, then  pass ownership of all files to user
RUN ./post_compile && \
    chmod 777 -R ./app/static && \
    chown -R $USER:$USER ./ && \
    rm -f ./post_compile

# get out of root and run container as user
USER $USER

# run the application server
CMD ["gunicorn", "--bind=0.0.0.0:5000", "wsgi:app"]

# =========================== Development ==============================
FROM dev-base AS development

# dummy development vars
ARG DEV_SECRET=dev
ARG DEV_ADMIN_EMAIL=admin@localhost

# hardcode env for development
ENV FLASK_ENV development
ENV ADMINS $DEV_ADMIN_EMAIL
ENV ADMIN_SECRET $DEV_SECRET
ENV CSP_REPORT_ONLY 1
ENV DEBUG_TB_ENABLED 0
ENV DEFAULT_MAIL_SENDER $DEV_ADMIN_EMAIL
ENV LOG_LEVEL DEBUG
ENV NAVBAR_HOME 0
ENV NAVBAR_ICONS 1
ENV NAVBAR_USER_DROPDOWN 1
ENV SECRET_KEY $DEV_SECRET
ENV SEND_FILE_MAX_AGE_DEFAULT 0
ENV BRAND "DevBrand"
ENV COPYRIGHT_AUTHOR "Dev Copyright Author"
ENV COPYRIGHT_EMAIL "dev_copyright_author@localhost.com"
ENV MAIL_SUBJECT_PREFIX "[DevBrand]: "

# execute command defined in docker-compose.yml within this script
COPY ./bin/entrypoint ./

# copy over prepared python virtualenv from builder
COPY --from=dev-backend-builder $VENV ./.venv

# pass ownership of all files to user
RUN chown -R $USER:$USER ./

# get out of root and run container as user
USER $USER

# ============================== Nginx =================================
FROM nginx:1.24-alpine AS nginx

# remove default config in `nginx` container
RUN rm /etc/nginx/conf.d/default.conf

# copy over prepared config
COPY ./nginx.conf /etc/nginx/conf.d

# copy over certs for serving https requests locally
COPY ./certs /etc/nginx/ssl
