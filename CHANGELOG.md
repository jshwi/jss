Changelog
=========
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

[Unreleased](https://github.com/jshwi/jss/compare/v1.4.0...HEAD)
------------------------------------------------------------------------
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
