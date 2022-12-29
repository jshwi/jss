"""
app.forms
=========

All classes derived from ``FlaskForm`` imported from ``Flask-WTF``.
``Flask-WTF`` is a ``Flask`` extension built on top of ``WTForms``.
"""
from flask import current_app
from flask_babel import lazy_gettext as _l
from flask_pagedown.fields import PageDownField
from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    PasswordField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    ValidationError,
)

from app.constants import PASSWORD, SUBMIT
from app.models import User


class RegistrationForm(FlaskForm):
    """Form for registering a new user."""

    username = StringField(
        _l("Username"), validators=[DataRequired(), Length(max=64)]
    )
    email = StringField(
        _l("Email"), validators=[DataRequired(), Email(), Length(max=120)]
    )
    password = PasswordField(_l(PASSWORD), validators=[DataRequired()])
    confirm_password = PasswordField(
        _l("Confirm Password"),
        validators=[DataRequired(), EqualTo("password")],
    )
    submit = SubmitField(_l("Register"))

    # noinspection PyMethodMayBeStatic
    def validate_username(self, username: StringField) -> None:
        """WTForms validates methods prefixed with ``validate_``.

        :param username: Username to check validity for.
        :raise: ValidationError if username already exists.
        """
        user = User.query.filter_by(username=username.data).first()
        reserved = username.data in current_app.config["RESERVED_USERNAMES"]
        if user is not None or reserved:
            raise ValidationError(_l("Username is taken"))

    # noinspection PyMethodMayBeStatic
    def validate_email(self, email: StringField) -> None:
        """WTForms validates methods prefixed with ``validate_``.

        :param email: Email to check validity for.
        :raise: ValidationError if user with email already exists.
        """
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(
                _l("A user with this email address is already registered")
            )


class LoginForm(FlaskForm):
    """Form for logging in an existing user."""

    username = StringField(_l("Username"), validators=[DataRequired()])
    password = PasswordField(_l(PASSWORD), validators=[DataRequired()])
    remember_me = BooleanField(_l("Remember Me"))
    submit = SubmitField(_l("Sign In"))


class PostForm(FlaskForm):
    """Form for creating new ``Post`` objects."""

    title = StringField(_l("Title"), validators=[DataRequired()])
    body = PageDownField(
        _l("Body"), validators=[DataRequired()], render_kw={"rows": 12}
    )
    submit = SubmitField(_l(SUBMIT))


class ResetPasswordRequestForm(FlaskForm):
    """Form for requesting a reset email for an existing user."""

    email = StringField(_l("Email"), validators=[DataRequired(), Email()])
    submit = SubmitField(_l("Request Password Reset"))


class ResetPasswordForm(FlaskForm):
    """Form for resetting an existing user's password."""

    password = PasswordField(_l(PASSWORD), validators=[DataRequired()])
    confirm_password = PasswordField(
        _l("Confirm Password"),
        validators=[DataRequired(), EqualTo(_l("password"))],
    )
    submit = SubmitField(_l("Reset Password"))


class EditProfile(FlaskForm):
    """Form for editing an existing user's profile page."""

    username = StringField(_l("username"), validators=[DataRequired()])
    about_me = TextAreaField(
        _l("About me"), validators=[Length(min=0, max=140)]
    )
    submit = SubmitField(_l(SUBMIT))


class EmptyForm(FlaskForm):
    """Empty form: Submit only."""

    submit = SubmitField(_l(SUBMIT))


class MessageForm(FlaskForm):
    """Form for creating new ``Message`` objects."""

    message = TextAreaField(
        _l("Message"), validators=[DataRequired(), Length(min=0, max=140)]
    )
    submit = SubmitField(_l(SUBMIT))
