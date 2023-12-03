# jss

[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build](https://github.com/jshwi/jss/actions/workflows/build.yaml/badge.svg)](https://github.com/jshwi/jss/actions/workflows/build.yaml)
[![CodeQL](https://github.com/jshwi/jss/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/jshwi/jss/actions/workflows/codeql-analysis.yml)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/jshwi/jss/master.svg)](https://results.pre-commit.ci/latest/github/jshwi/jss/master)
[![codecov.io](https://codecov.io/gh/jshwi/jss/branch/master/graph/badge.svg)](https://codecov.io/gh/jshwi/jss)
[![readthedocs.org](https://readthedocs.org/projects/jss/badge/?version=latest)](https://jss.readthedocs.io/en/latest/?badge=latest)
[![python3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380)
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![docformatter](https://img.shields.io/badge/%20formatter-docformatter-fedcba.svg)](https://github.com/PyCQA/docformatter)
[![prettier](https://img.shields.io/badge/code_style-prettier-ff69b4.svg?style=flat-square)](https://github.com/prettier/prettier)
[![pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/PyCQA/pylint)
[![Security Status](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![Known Vulnerabilities](https://snyk.io/test/github/jshwi/jss/badge.svg)](https://snyk.io/test/github/jshwi/jss/badge.svg)

## A Flask webapp

### Install

```shell
  $ docker compose build
```

### Development

http://localhost:5000

```shell
  $ npm run init:dev
  $ docker compose up dev
```

### Production

https://localhost:443

```shell
  $ docker compose up production
```

## Documentation

- Source documentation [here](https://jshwi.github.io/jss/)

## Features

### Progressive Web Application

- Mobile support
- Installable as a standalone app

### User Accounts

- Single admin user (Can only be created by root user via the commandline)
  - Access to site configuration
    - change favicon
  - Access to UI for viewing database
- Signing up
  - Email verification
- Log in
  - Password reset functionality
- Logged in (including admin)
  - Editable user profiles
  - Functionality to follow other users
  - Functionality to message other users
  - Allow changing of username (while still being able to find user by old username)

### Blog Posts

- CREATE, READ, UPDATE, DELETE, or "CRUD"
- Posting, updating, and deleting posts restricted to authorized users
- All posts are timestamped
- Markdown support with syntax highlighting (see list of languages [here](https://github.com/jshwi/jss/blob/master/.github/LEXERS.md))
- Pagination support
- Support for versioning and rolling back changes

### Configurable

- Toggle dark mode

### Translation

- See list of languages [here](https://github.com/jshwi/jss/blob/master/app/translations/LANGUAGES.md)

### Integrations

- Stripe payment option
- Gravatar for user avatars

### Error handling

- Support for emailing errors
