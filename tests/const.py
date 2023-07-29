"""
tests.const
===========
"""
from datetime import datetime

UPDATE1 = "/post/1/update"
ADMIN_USER_USERNAME = "admin"
ADMIN_USER_EMAIL = "admin@test.com"
ADMIN_USER_PASSWORD = "pass0"
AUTHORIZED_USER_USERNAME = "authorized"
AUTHORIZED_USER_EMAIL = "authorized@test.com"
AUTHORIZED_USER_PASSWORD = "pass1"
MAIN_USER_USERNAME = "main"
MAIN_USER_EMAIL = "main@test.com"
MAIN_USER_PASSWORD = "pass2"
OTHER_USER_USERNAME = "other"
OTHER_USER_EMAIL = "other@test.com"
OTHER_USER_PASSWORD = "pass3"
LAST_USER_USERNAME = "last"
LAST_USER_EMAIL = "last@test.com"
LAST_USER_PASSWORD = "pass4"
POST_TITLE_1 = "test title 1"
POST_BODY_1 = "test 1\nbody 1"
POST_AUTHOR_ID_1 = 1
POST_TITLE_2 = "test title 2"
POST_BODY_2 = "test 2\nbody 2"
POST_AUTHOR_ID_2 = 2
POST_TITLE_3 = "test title 3"
POST_BODY_3 = "test 3\nbody 3"
POST_AUTHOR_ID_3 = 3
POST_TITLE_4 = "test title 4"
POST_BODY_4 = "test 4\nbody 4"
POST_AUTHOR_ID_4 = 4
POST_TITLE_V1 = "title-v1"
POST_TITLE_V2 = "body-v1"
POST_BODY_V1 = "title-v2"
POST_BODY_V2 = "body-v2"
POST_TITLE_V3 = "title-v3"
POST_BODY_V3 = "body-v3"
POST_CREATED_1 = datetime(2018, 1, 1, 0, 0, 1)
POST_CREATED_2 = datetime(2018, 1, 1, 0, 0, 2)
POST_CREATED_3 = datetime(2018, 1, 1, 0, 0, 3)
POST_CREATED_4 = datetime(2018, 1, 1, 0, 0, 4)
MESSAGE_CREATED = datetime(2018, 1, 1, 0, 0, 5)
INVALID_OR_EXPIRED = "invalid or has expired."
MAIL_SERVER = "localhost"
MAIL_USERNAME = MAIN_USER_USERNAME
MAIL_PASSWORD = "unique"
MAIL_PORT = 25
PROFILE_EDIT = "/user/profile/edit"
ADMIN_ROUTE = "/admin"
ADMIN_USER_ROUTE = "/admin/users"
COPYRIGHT_YEAR = "2023"
COPYRIGHT_AUTHOR = "John Doe"
COPYRIGHT_EMAIL = "john.doe@test.com"
RECIPIENT_ID = 1
SENDER_ID = 2
MESSAGE_BODY = "hello, this is a test message"
REDIRECT_LOGOUT = "/redirect/logout"
POST_1 = "/post/1"
APP_UTILS_LANG_SUBPROCESS_RUN = "app.cli.translate.subprocess.run"
MESSAGES_POT = "messages.pot"
MESSAGES_PO = "messages.po"
LICENSE = "LICENSE"
USERNAME_IS_TAKEN = b"Username is taken"
COMPILE = "compile"
INIT = "init"
PYBABEL = "pybabel"
USER = "user"
USERNAME = "username"
LOCATION = "Location"
NAVBAR_HOME = "NAVBAR_HOME"
CREATE = "create"
TRANSLATE = "translate"
INIT_DB = "init_db"
POST = "post"
TRANSLATIONS_DIR = "TRANSLATIONS_DIR"
TITLE = "title"
LOGOUT = "Logout"
ROUTE = "route"
POST_1_DELETE = "/post/1/delete"
ADMIN = "admin"
POST_CREATE = "/post/create"
BODY = "body"
PYPROJECT_TOML = f"""\
[tool.poetry]
authors = [
    "jshwi <{COPYRIGHT_EMAIL}>",
]
description = "A Flask webapp"
keywords = [
    "flask",
    "webapp",
    "pwa",
    "jshwisolutions",
    "blog",
]
license = "MIT"
name = "jss"
packages = [{{ include = "app" }}]
readme = "README.rst"
version = "1.16.2"
"""
STATUS_CODE_TO_ROUTE_DEFAULT = [
    (
        200,  # all OK
        [
            "/",
            "/auth/login",
            "/auth/register",
            "/auth/request_password_reset",
            "/post/<int:id>",
            "/profile/<username>",
            "/auth/logout",
            "/auth/reset_password/<token>",
            "/order/success",
            "/order/cancel",
            "/favicon.ico",
        ],
    ),
    (
        401,  # unauthorized,
        [
            "/admin/",
            "/redirect/<token>",
            "/redirect/resend",
            "/auth/unconfirmed",
            "/post/create",
            "/redirect/export_posts",
            "/user/messages",
            "/user/profile/edit",
            "/user/send_message/<recipient>",
            "/user/messages",
            "/user/notifications",
            "/post/<int:id>/update",
        ],
    ),
    (
        405,  # method not allowed
        [
            "/redirect/follow/<username>",
            "/redirect/unfollow/<username>",
            "/post/<int:id>/delete",
            "/report/csp_violations",
            "/order/call",
        ],
    ),
]
COVERED_ROUTES = [r for _, l in STATUS_CODE_TO_ROUTE_DEFAULT for r in l]
POT_CONTENTS = """
# Translations template for PROJECT.
# Copyright (C) 2022 ORGANIZATION
# This file is distributed under the same license as the PROJECT project.
# FIRST AUTHOR <EMAIL@ADDRESS>, 2022.
#
#, fuzzy
msgid ""
msgstr ""
"Project-Id-Version: PROJECT VERSION\\n"
"Report-Msgid-Bugs-To: EMAIL@ADDRESS\\n"
"POT-Creation-Date: 2022-06-02 14:34+1000\\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"
"Language-Team: LANGUAGE <LL@li.org>\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=utf-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Generated-By: Babel 2.10.1\\n"

#: app/forms.py:34 app/forms.py:75
msgid "Username"
msgstr ""

#: app/forms.py:37 app/forms.py:94
msgid "Email"
msgstr ""

#: app/forms.py:39 app/forms.py:76 app/forms.py:101
msgid "Password"
msgstr ""

#: app/forms.py:41 app/forms.py:103
msgid "Confirm Password"
msgstr ""

#: app/dom/navbar.py:90 app/forms.py:44 app/templates/auth/register.html:6
msgid "Register"
msgstr ""

#: app/forms.py:56
msgid "Username is taken"
msgstr ""

#: app/forms.py:68
msgid "A user with this email address is already registered"
msgstr ""

#: app/forms.py:77
msgid "Remember Me"
msgstr ""

#: app/forms.py:78 app/templates/auth/login.html:6
msgid "Sign In"
msgstr ""

#: app/forms.py:84
msgid "Title"
msgstr ""

#: app/forms.py:86
msgid "Body"
msgstr ""

#: app/forms.py:88 app/forms.py:116 app/forms.py:122 app/forms.py:131
msgid "Submit"
msgstr ""

#: app/forms.py:95
msgid "Request Password Reset"
msgstr ""

#: app/forms.py:104
msgid "password"
msgstr ""

#: app/forms.py:106 app/templates/auth/reset_password.html:6
msgid "Reset Password"
msgstr ""

#: app/forms.py:112
msgid USERNAME
msgstr ""

#: app/forms.py:114
msgid "About me"
msgstr ""

#: app/forms.py:129
msgid "Message"
msgstr ""

#: app/dom/macros.py:51
msgid "Versions"
msgstr ""

#: app/dom/macros.py:131
msgid "Previous"
msgstr ""

#: app/dom/macros.py:142
msgid "Next"
msgstr ""

#: app/dom/navbar.py:25 app/templates/user/messages.html:7
msgid "Messages"
msgstr ""

#: app/dom/navbar.py:42
msgid "Profile"
msgstr ""

#: app/dom/navbar.py:44
msgid LOGOUT
msgstr ""

#: app/dom/navbar.py:48
msgid "Console"
msgstr ""

#: app/dom/navbar.py:49
msgid "RQ Dashboard"
msgstr ""

#: app/dom/navbar.py:68
msgid "Home"
msgstr ""

#: app/dom/navbar.py:76
msgid "New"
msgstr ""

#: app/dom/navbar.py:91
msgid "Login"
msgstr ""

#: app/views/redirect.py:44
msgid "Account already confirmed. Please login."
msgstr ""

#: app/views/redirect.py:50
msgid "Your account has been verified."
msgstr ""

#: app/views/redirect.py:53
msgid "The confirmation link is invalid or has expired."
msgstr ""

#: app/views/redirect.py:80
msgid "A new confirmation email has been sent."
msgstr ""

#: app/views/redirect.py:121
#, python-format
msgid "You are now following %(username)s"
msgstr ""

#: app/views/redirect.py:144
#, python-format
msgid "You are no longer following %(username)s"
msgstr ""

#: app/views/redirect.py:162
msgid "An export task is already in progress"
msgstr ""

#: app/templates/posts.html:23 app/templates/public/profile.html:35
msgid "Edit"
msgstr ""

#: app/templates/auth/login.html:16
msgid "New User?"
msgstr ""

#: app/templates/auth/login.html:16
msgid "Click to Register!"
msgstr ""

#: app/templates/auth/login.html:19
msgid "Forgot password?"
msgstr ""

#: app/templates/auth/register.html:16
msgid "Already a User?"
msgstr ""

#: app/templates/auth/register.html:16
msgid "Click to Sign In!"
msgstr ""

#: app/templates/auth/request_password_reset.html:6
msgid "Password Reset"
msgstr ""

#: app/templates/auth/request_password_reset.html:10
msgid "Please enter your email to receive a password reset link"
msgstr ""

#: app/templates/auth/reset_password.html:10
msgid "Please enter your new password"
msgstr ""

#: app/templates/auth/unconfirmed.html:5
msgid "Account Verification Pending"
msgstr ""

#: app/templates/auth/unconfirmed.html:9
msgid "Please check your inbox or junk folder for a confirmation link."
msgstr ""

#: app/templates/auth/unconfirmed.html:12
msgid "Didn't get the email?"
msgstr ""

#: app/templates/auth/unconfirmed.html:12
msgid "Resend"
msgstr ""

#: app/templates/email/activate.html:1
msgid "Please follow the below link to activate your account"
msgstr ""

#: app/templates/email/reset_password.html:1
msgid "Hi"
msgstr ""

#: app/templates/email/reset_password.html:2
msgid "To reset your password click on the following link"
msgstr ""

#: app/templates/email/reset_password.html:3
msgid "Reset password"
msgstr ""

#: app/templates/email/reset_password.html:4
msgid ""
"If you have not requested a password reset you can simply ignore this "
"message"
msgstr ""

#: app/templatesPOST_CREATE.html:6
msgid "New Post"
msgstr ""

#: app/templates/post/read.html:19
msgid "Update"
msgstr ""

#: app/templates/post/read.html:21
msgid "Restore"
msgstr ""

#: app/templates/post/update.html:7
msgid "Edit Post"
msgstr ""

#: app/templates/post/update.html:15
msgid "Delete"
msgstr ""

#: app/templates/public/index.html:7
msgid "Posts"
msgstr ""

#: app/templates/public/profile.html:21
msgid "Last seen on"
msgstr ""

#: app/templates/public/profile.html:29
msgid "followers"
msgstr ""

#: app/templates/public/profile.html:29
msgid "following."
msgstr ""

#: app/templates/public/profile.html:39
msgid "Export posts"
msgstr ""

#: app/templates/public/profile.html:43
msgid "Send private message"
msgstr ""

#: app/templates/public/profile.html:49
msgid "Follow"
msgstr ""

#: app/templates/public/profile.html:56
msgid "Unfollow"
msgstr ""

#: app/templates/user/edit_profile.html:6
msgid "Edit Profile"
msgstr ""

#: app/templates/user/send_message.html:6
msgid "Send Message to"
msgstr ""

"""
LICENSE_CONTENTS = f"""\
MIT License

Copyright (c) {COPYRIGHT_YEAR} {COPYRIGHT_AUTHOR}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
