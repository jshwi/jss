Changelog
=========
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

[Unreleased](https://github.com/jshwi/jss/compare/v1.13.3...HEAD)
------------------------------------------------------------------------

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
