Changelog
=========
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

[Unreleased](https://github.com/jshwi/jss/compare/v0.1.0...HEAD)
------------------------------------------------------------------------
### Added
- Adds admin user
- Adds `create user` function to cli
- Adds user module
- Adds mail module
- Adds mandatory email field for registration

### Changed
- Removes posting for all users as default
- Adds `Flask-Login` for handling logins
- Moves database over to `SQLAlchemy`
