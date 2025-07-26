Changelog
=========
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

[Unreleased](https://github.com/jshwi/jss/compare/v1.36.7...HEAD)
------------------------------------------------------------------------

[1.36.7](https://github.com/jshwi/jss/releases/tag/v1.36.7) - 2025-07-26
------------------------------------------------------------------------
### Fixed
- add .python-version for build

[1.36.6](https://github.com/jshwi/jss/releases/tag/v1.36.6) - 2025-07-26
------------------------------------------------------------------------
### Security
- Update vulnerable dependencies

[1.36.5](https://github.com/jshwi/jss/releases/tag/v1.36.5) - 2024-10-18
------------------------------------------------------------------------
### Security
- Update vulnerable dependencies

[1.36.4](https://github.com/jshwi/jss/releases/tag/v1.36.4) - 2024-08-02
------------------------------------------------------------------------
### Security
- Update vulnerable dependencies

[1.36.3](https://github.com/jshwi/jss/releases/tag/v1.36.3) - 2024-05-15
------------------------------------------------------------------------
### Fixed
- revert css-loader and not bootstrap-icons to fix broken icons

[1.36.2](https://github.com/jshwi/jss/releases/tag/v1.36.2) - 2024-05-15
------------------------------------------------------------------------
### Fixed
- broken icons

[1.36.1](https://github.com/jshwi/jss/releases/tag/v1.36.1) - 2024-05-15
------------------------------------------------------------------------
### Security
- Update vulnerable dependencies

[1.36.0](https://github.com/jshwi/jss/releases/tag/v1.36.0) - 2023-12-05
------------------------------------------------------------------------
### Changed
- only add users that are authorized to sitemap

[1.35.0](https://github.com/jshwi/jss/releases/tag/v1.35.0) - 2023-12-05
------------------------------------------------------------------------
### Added
- add profiles to sitemap
- index to sitemap generator
- sitemap change freq to config

### Changed
- use https by default for sitemap
- remove items that do not need to be on sitemap by default

[1.34.0](https://github.com/jshwi/jss/releases/tag/v1.34.0) - 2023-12-04
------------------------------------------------------------------------
### Added
- posts to sitemap

[1.33.0](https://github.com/jshwi/jss/releases/tag/v1.33.0) - 2023-12-03
------------------------------------------------------------------------
### Added
- ini support for fenced code

[1.32.0](https://github.com/jshwi/jss/releases/tag/v1.32.0) - 2023-08-09
------------------------------------------------------------------------
### Added
- add `SCHEMAS` config variable
- add `app.config.Config`
- add `app.cli.translate.readme`
- add `app.cli.translate.init`
- add `app.cli.translate.compile`
- add `app.cli.translate.update`
- add `app.cli.lexer.readme`
- add `app.cli.create.admin`
- add `app.cli.create.user`
- add sitemap

### Changed
- move creation of uploads dir to filesystem module
- remove creation of `STATIC_FOLDER` on setting
- rename `app.utils` to `app.fs`
- add default value for `DATABASE_URL`
- update `CSPType` to refer to `ContentSecurityPolicy`

### Fixed
- fix display of avatar on user profile

### Removed
- remove `PYPROJECT_TOML` config variable
- remove `LICENSE` config variable
- remove `CSP_REPORT_URI` config variable
- remove `REDIS_URL` config variable
- remove `MAIL_DEBUG` config variable
- remove `FLASK_STATIC_DIGEST_GZIP_FILES` config variable
- remove `CACHE_TYPE` config variable

[1.31.0](https://github.com/jshwi/jss/releases/tag/v1.31.0) - 2023-08-01
------------------------------------------------------------------------
### Added
- add `STATIC_FOLDER` environment variable

### Fixed
- ensure configured favicon resolves to `UPLOAD_PATH`

[1.30.0](https://github.com/jshwi/jss/releases/tag/v1.30.0) - 2023-07-30
------------------------------------------------------------------------
### Added
- add upload favicon functionality to admin interface
- add /admin endpoint

### Changed
- change /admin endpoint to /database
- rename `Console` to `Database`
- position footer at bottom of page

### Fixed
- remove `fontawesome.bundle.js` which does not exist

[1.29.0](https://github.com/jshwi/jss/releases/tag/v1.29.0) - 2023-07-28
------------------------------------------------------------------------
### Changed
- import bootstrap.min.css
- add `runtime` bundle
- make `MyModelView` private

### Fixed
- fix favicon

[1.28.0](https://github.com/jshwi/jss/releases/tag/v1.28.0) - 2023-07-26
------------------------------------------------------------------------
### Changed
- remove `fortawesome` from css bundle
- add bootstrap_toggle bundle
- add bootstrap bundle
- add messages bundle
- add highlight bundle

[1.27.0](https://github.com/jshwi/jss/releases/tag/v1.27.0) - 2023-07-26
------------------------------------------------------------------------
### Added
- add stripe payment option
- add icon for login
- add optional display of register on navbar
- add `TITLE` config variable
- add optional display of posts

[1.26.0](https://github.com/jshwi/jss/releases/tag/v1.26.0) - 2023-07-25
------------------------------------------------------------------------
### Changed
- ensure `POT-Creation-Date` is not included in translation headers
- remove `POT-Creation-Date` from translation headers

### Fixed
- fix Spanish translations

### Removed
- remove `BABEL_FILENAME` config variable

[1.25.0](https://github.com/jshwi/jss/releases/tag/v1.25.0) - 2023-07-23
------------------------------------------------------------------------
### Changed
- remove reliance on `FLASK_ENV` for testing

### Removed
- remove `FLASK_ENV`

[1.24.2](https://github.com/jshwi/jss/releases/tag/v1.24.2) - 2023-07-20
------------------------------------------------------------------------
### Fixed
- change prefix for default `SQLALCHEMY_DATABASE_URI`

[1.24.1](https://github.com/jshwi/jss/releases/tag/v1.24.1) - 2023-07-14
------------------------------------------------------------------------
### Security
- update `flask`
- run audit on `npm` packages

[1.24.0](https://github.com/jshwi/jss/releases/tag/v1.24.0) - 2023-07-14
------------------------------------------------------------------------
### Changed
- remove `logdna` addon
- remove `heroku-redis` addon
- remove worker dyno

[1.23.0](https://github.com/jshwi/jss/releases/tag/v1.23.0) - 2023-07-10
------------------------------------------------------------------------
### Added
- add app.json

### Changed
- bump heroku stack

[1.22.0](https://github.com/jshwi/jss/releases/tag/v1.22.0) - 2023-07-10
------------------------------------------------------------------------
### Removed
- remove task worker

[1.21.3](https://github.com/jshwi/jss/releases/tag/v1.21.3) - 2023-07-09
------------------------------------------------------------------------
### Security
- Update vulnerable dependencies

[1.21.2](https://github.com/jshwi/jss/releases/tag/v1.21.2) - 2023-05-12
------------------------------------------------------------------------
### Security
- Bump cryptography from 38.0.4 to 39.0.1
- Bump werkzeug from 2.0.3 to 2.3.4

[1.21.1](https://github.com/jshwi/jss/releases/tag/v1.21.1) - 2023-01-07
------------------------------------------------------------------------
### Security
- Update vulnerable dependencies

[1.21.0](https://github.com/jshwi/jss/releases/tag/v1.21.0) - 2023-01-05
------------------------------------------------------------------------
### Added
- Add py.typed

### Security
- Add `usedforsecurity=False` to `hashlib`'

[1.20.5](https://github.com/jshwi/jss/releases/tag/v1.20.5) - 2022-11-16
------------------------------------------------------------------------
### Security
- Bumps `loader-utils` from 2.0.3 to 2.0.4

[1.20.4](https://github.com/jshwi/jss/releases/tag/v1.20.4) - 2022-11-09
------------------------------------------------------------------------
### Security
- Pins `cryptography` version to ^38.0.3
- Bumps `loader-utils` from 2.0.2 to 2.0.3

[1.20.3](https://github.com/jshwi/jss/releases/tag/v1.20.3) - 2022-08-07
------------------------------------------------------------------------
### Fixed
- Fixes `/static/site.webmanifest`

[1.20.2](https://github.com/jshwi/jss/releases/tag/v1.20.2) - 2022-08-07
------------------------------------------------------------------------
### Fixed
- Adds `six` to `dependencies`

[1.20.1](https://github.com/jshwi/jss/releases/tag/v1.20.1) - 2022-08-07
------------------------------------------------------------------------
### Security
- Runs `npm audit fix`
- Removes `webpack-pwa-manifest` from `devDependencies`

[1.20.0](https://github.com/jshwi/jss/releases/tag/v1.20.0) - 2022-07-01
------------------------------------------------------------------------
### Changed
- Moves `/redirect/<int:id>/delete` to `/post/<int:id>/delete`

### Fixed
- Removes update link for incorrect user in `/post/<int:id>`

[1.19.1](https://github.com/jshwi/jss/releases/tag/v1.19.1) - 2022-06-04
------------------------------------------------------------------------
### Fixed
- Adds `npm run build` script

[1.19.0](https://github.com/jshwi/jss/releases/tag/v1.19.0) - 2022-06-02
------------------------------------------------------------------------
### Added
- Adds Spanish translation
- Adds support for language translations
- Adds `ADMIN_SECRET` to config

[1.18.1](https://github.com/jshwi/jss/releases/tag/v1.18.1) - 2022-05-31
------------------------------------------------------------------------
### Fixed
- Removes translate process from bin/post_compile

[1.18.0](https://github.com/jshwi/jss/releases/tag/v1.18.0) - 2022-05-31
------------------------------------------------------------------------
### Changed
- Removes rotating file logger
- Implements config for email signature
- Updates commandline help
- Replaces `Bootstrap` with `Bootstrap4`

### Fixed
- Fixes progress in `app.utils.tasks._set_task_progress`

[1.17.0](https://github.com/jshwi/jss/releases/tag/v1.17.0) - 2022-05-27
------------------------------------------------------------------------
### Changed
- Moves compiled static assets from /static/build/ to /static/
- Updates `COPYRIGHT_EMAIL` default value

[1.16.2](https://github.com/jshwi/jss/releases/tag/v1.16.2) - 2022-05-11
------------------------------------------------------------------------
### Security
- Removes `Flask-Caching`

[1.16.1](https://github.com/jshwi/jss/releases/tag/v1.16.1) - 2022-04-30
------------------------------------------------------------------------
### Security
- Upgrades dependencies

[1.16.0](https://github.com/jshwi/jss/releases/tag/v1.16.0) - 2022-03-06
------------------------------------------------------------------------
### Added
- Adds `yaml` support for fenced code
- Adds `shell` support for fenced code

[1.15.1](https://github.com/jshwi/jss/releases/tag/v1.15.1) - 2022-03-06
------------------------------------------------------------------------
### Fix
- Reverts prior to 5039f7 as `PurgeCSSPlugin` removed valid CSS

[1.15.0](https://github.com/jshwi/jss/releases/tag/v1.15.0) - 2022-03-06
------------------------------------------------------------------------
### Change
- Increases service worker precache maximum to 3000000 bytes

### Fixed
- Removes unused css from bundle

### Security
- Updates CSP

[1.14.0](https://github.com/jshwi/jss/releases/tag/v1.14.0) - 2022-03-05
------------------------------------------------------------------------
### Changed
- Lessens contrast when hovering over posts
- Displays "Restore" button only if other revision
- Enlarges dark mode toggle button

### Security
- Updates CSP

[1.13.4](https://github.com/jshwi/jss/releases/tag/v1.13.4) - 2022-02-26
------------------------------------------------------------------------
### Changed
- Migrates over to `poetry` from `pipenv`

[1.13.3](https://github.com/jshwi/jss/releases/tag/v1.13.3) - 2021-12-06
------------------------------------------------------------------------
### Fixed
- Rewinds Procfile prior to a9f703

[1.13.2](https://github.com/jshwi/jss/releases/tag/v1.13.2) - 2021-12-06
------------------------------------------------------------------------
### Fixed
- Removes `static:compile` from release script

[1.13.1](https://github.com/jshwi/jss/releases/tag/v1.13.1) - 2021-12-06
------------------------------------------------------------------------
### Fixed
- Adds `node` version to package.json `engines` key

[1.13.0](https://github.com/jshwi/jss/releases/tag/v1.13.0) - 2021-12-06
------------------------------------------------------------------------
### Added
- Compresses served files with `Flask-Compress`
- Implements `workbox` to handle service worker
- Implements `webpack` for bundling static files and library

### Changed
- Adds `moment` inline to `webpack` bundle

### Fixed
- Fixes email typo
- Fixes `Lighthouse` meta-description audit
- Fixes `Lighthouse` maskable icon audit
- Fixes up handling of icons

### Security
Updates CSP

[1.12.1](https://github.com/jshwi/jss/releases/tag/v1.12.1) - 2021-11-24
------------------------------------------------------------------------
### Fixed
- Properly renders post markdown

[1.12.0](https://github.com/jshwi/jss/releases/tag/v1.12.0) - 2021-11-22
------------------------------------------------------------------------
### Added
- Adds browserconfig.xml
- Adds .webmanifest
- Adds additional favicon types
- Adds additional meta tags

### Changed
- Serves favicon from root of application
- Adds more mobile-friendly footer
- Changes Restore button to `btn-primary`
- Changes Delete button to `btn-danger`
- Rounds navbar avatar
- Aligns navbar items
- Updates rows for mobile viewing
- Adds `DarkReader` CDN; Writes `DarkReader` directly into app
- change: Updates footer for `Bootstrap 4`
- Renames pagination links
- Updates pagination for `Bootstrap 4`
- Updates navbar for `Bootstrap 4`
- Swaps `navbar-brand` with `toggle-darkreader`
- Adds `DarkReader` toggle to navbar permanently
- Replaces inheritance of `BootstrapRenderer` with `Visitor`

### Fixed
- Fixes dropdown from displaying left on profile
- Fixes fenced code highlighting

[1.11.0](https://github.com/jshwi/jss/releases/tag/v1.11.0) - 2021-11-13
------------------------------------------------------------------------
### Security
- Adds default CSP exception for day/night mode

[1.10.0](https://github.com/jshwi/jss/releases/tag/v1.10.0) - 2021-11-12
------------------------------------------------------------------------
### Added
- `app.utils.csp` with `ContentSecurityPolicy`, `CSPType`, and `CSPValType`

### Security
- Fixes inline style for current version dropdown
- Fixes inline style for notification button
- Renders `moment.js` for inline nonce
- Adds inline nonce for `script-src-elem`
- Moves inline style to app/static/css/static.css for `user-post-td`
- Adds default Content Security Policy

[1.9.0](https://github.com/jshwi/jss/releases/tag/v1.9.0) - 2021-11-10
------------------------------------------------------------------------
### Changed
- Moves `app.utils.models._BaseModel` to public scope

### Fixed
- Fixes `Flask` without `Gunicorn` debug logging
- Changes blueprint name from `views` to `public`

[1.8.2](https://github.com/jshwi/jss/releases/tag/v1.8.2) - 2021-11-09
------------------------------------------------------------------------
### Fixed
- Fixes `url_for` for outdated paths

[1.8.1](https://github.com/jshwi/jss/releases/tag/v1.8.1) - 2021-11-08
------------------------------------------------------------------------
### Fixed
- Integrates `Flask` logger with `Gunicorn` logger

[1.8.0](https://github.com/jshwi/jss/releases/tag/v1.8.0) - 2021-11-08
------------------------------------------------------------------------
### Added
- Adds CSP violation reporting
- Adds `PREFERRED_URL_SCHEME` config; defaults to `"https"`

### Fixed
- Logs error descriptions

### Security
- Replaces `secure` headers with `Flask-Talisman` headers

[1.7.4](https://github.com/jshwi/jss/releases/tag/v1.7.4) - 2021-11-08
------------------------------------------------------------------------
### Added
- Adds CSP violation reporting
- Adds `PREFERRED_URL_SCHEME` config; defaults to `"https"`

### Fixed
- Logs error descriptions

### Security
- Replaces `secure` headers with `Flask-Talisman` headers

[1.7.3](https://github.com/jshwi/jss/releases/tag/v1.7.3) - 2021-11-03
------------------------------------------------------------------------
### Security
- Removes information disclosure comments
- Secures cookies
- Adds security headers

[1.7.2](https://github.com/jshwi/jss/releases/tag/v1.7.2) - 2021-11-02
------------------------------------------------------------------------
### Changed
- Removes trailing slash from update route
- Implements query-string for revision updates
- Removes arrows from post navigation footer
- Disables `vX: This revision` link in version dropdown
- Formats rendered HTML

[1.7.1](https://github.com/jshwi/jss/releases/tag/v1.7.1) - 2021-11-01
------------------------------------------------------------------------
### Changed
- Updates route `/post/post/<int:id>` to `/post/<int:id>`
- Prefixes post routes with /post
- Prefixes user routes with /user
- Prefixes redirects with /redirect
- Updates route names for /admin

[1.7.0](https://github.com/jshwi/jss/releases/tag/v1.7.0) - 2021-10-24
------------------------------------------------------------------------
### Added
- Adds `NAVBAR_USER_DROPDOWN` to config
- Adds `NAVBAR_ICONS` to config
- Adds `NAVBAR_HOME` to config
- Adds dark mode toggle

### Changed
- change: Moves `New[Post]` link to navbar
- Changes nav container to fluid
- Implements hashed node ID for navbar

[1.6.2](https://github.com/jshwi/jss/releases/tag/v1.6.2) - 2021-10-19
------------------------------------------------------------------------
### Fixed
- Sets max length for username and email in registration form

[1.6.1](https://github.com/jshwi/jss/releases/tag/v1.6.1) - 2021-10-17
------------------------------------------------------------------------
### Fixed
- Footer pushed to bottom of page

[1.6.0](https://github.com/jshwi/jss/releases/tag/v1.6.0) - 2021-10-15
------------------------------------------------------------------------
### Added
- Adds favicon

[1.5.0](https://github.com/jshwi/jss/releases/tag/v1.5.0) - 2021-10-15
------------------------------------------------------------------------
### Added
- Adds footer
- Adds `LICENSE` to config
- Adds`SETUP_FILE` to config
- Adds `COPYRIGHT` to config
- Adds `COPYRIGHT_YEAR` to config
- Adds `COPYRIGHT_AUTHOR` to config
- Adds `COPYRIGHT_EMAIL` to config

### Changed
- Removes `app.post` for `Post` class method

[1.4.0](https://github.com/jshwi/jss/releases/tag/v1.4.0) - 2021-10-15
------------------------------------------------------------------------
### Added
- Adds `BRAND` to config
- Restores version through /update

### Changed
- Configures `app.jinja_env`

[1.3.0](https://github.com/jshwi/jss/releases/tag/v1.3.0) - 2021-10-11
------------------------------------------------------------------------
### Added
- Adds `RESERVED_USERNAMES` to config

[1.2.0](https://github.com/jshwi/jss/releases/tag/v1.2.0) - 2021-10-11
------------------------------------------------------------------------
### Added
- Allows user with changed name to be referenced by old name

### Fixed
- Returns ``404: Not Found`` for non-existing user

[1.1.2](https://github.com/jshwi/jss/releases/tag/v1.1.2) - 2021-10-05
------------------------------------------------------------------------
### Fixed
- Fixes crash from occurring when user accesses /admin route whilst not logged in


[1.1.1](https://github.com/jshwi/jss/releases/tag/v1.1.1) - 2021-10-04
------------------------------------------------------------------------
### Fixed
- Authorized users can now CREATE, READ, UPDATE, and DELETE posts

[1.1.0](https://github.com/jshwi/jss/releases/tag/v1.1.0) - 2021-10-04
------------------------------------------------------------------------
### Added
- Adds `Flask-Admin`
- Adds `403 Forbidden` page
- Adds `User.authorized`
- Adds versioning for posts

### Fixed
- `Task` inherits from `_BaseModel`

[1.0.1](https://github.com/jshwi/jss/releases/tag/v1.0.1) - 2021-10-03
------------------------------------------------------------------------
### Fixed
- Adds `page_name` block to base.html
- Removes form data from title

[1.0.0](https://github.com/jshwi/jss/releases/tag/v1.0.0) - 2021-10-02
------------------------------------------------------------------------
### Added
- Adds `Task` model
- Adds syntax highlighting to fenced code
- Adds `Moment.js`
- Adds pagination of posts
- Adds `Bootstrap`
- Adds support for markdown
- Adds follow functionality
- Adds edit profile page
- Records user's last login time
- Adds page to display individual posts
- Adds user profiles
- Adds user avatars
- Adds error logging email handler
- Adds reset password functionality
- Adds email verification
- Adds admin user
- Adds `create user` function to cli
- Adds user module
- Adds mail module
- Adds mandatory email field for registration

### Changed
- Adds `Flask-WTF` for handling forms
- Removes posting for all users as default
- Adds `Flask-Login` for handling logins
- Moves database over to `SQLAlchemy`
