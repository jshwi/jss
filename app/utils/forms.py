"""
app.utils.forms
===============

All classes derived from ``FlaskForm`` imported from ``Flask-WTF``.
``Flask-WTF`` is a ``Flask`` extension built on top of ``WTForms``.
"""
from flask import current_app
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

from app.models import User


class RegistrationForm(FlaskForm):
    """Form for registering a new user."""

    username = StringField(
        "Username", validators=[DataRequired(), Length(max=64)]
    )
    email = StringField(
        "Email", validators=[DataRequired(), Email(), Length(max=120)]
    )
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Register")

    # noinspection PyMethodMayBeStatic
    def validate_username(  # pylint: disable=no-self-use
        self, username: StringField
    ) -> None:
        """WTForms validates methods prefixed with ``validate_``.

        :param username: Username to check validity for.
        :raise: ValidationError if username already exists.
        """
        user = User.query.filter_by(username=username.data).first()
        reserved = username.data in current_app.config["RESERVED_USERNAMES"]
        if user is not None or reserved:
            raise ValidationError("Username is taken")

    # noinspection PyMethodMayBeStatic
    def validate_email(  # pylint: disable=no-self-use
        self, email: StringField
    ) -> None:
        """WTForms validates methods prefixed with ``validate_``.

        :param email: Email to check validity for.
        :raise: ValidationError if user with email already exists.
        """
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(
                "A user with this email address is already registered"
            )


class LoginForm(FlaskForm):
    """Form for logging in an existing user."""

    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class PostForm(FlaskForm):
    """Form for creating new ``Post`` objects."""

    title = StringField("Title", validators=[DataRequired()])
    body = PageDownField(
        "Body", validators=[DataRequired()], render_kw={"rows": 12}
    )
    submit = SubmitField("Submit")


class ResetPasswordRequestForm(FlaskForm):
    """Form for requesting a reset email for an existing user."""

    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Request Password Reset")


class ResetPasswordForm(FlaskForm):
    """Form for resetting an existing user's password."""

    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Reset Password")


class EditProfile(FlaskForm):
    """Form for editing an existing user's profile page."""

    username = StringField("username", validators=[DataRequired()])
    about_me = TextAreaField("About me", validators=[Length(min=0, max=140)])
    submit = SubmitField("Submit")


class EmptyForm(FlaskForm):
    """Empty form: Submit only."""

    submit = SubmitField("Submit")


class MessageForm(FlaskForm):
    """Form for creating new ``Message`` objects."""

    message = TextAreaField(
        "Message", validators=[DataRequired(), Length(min=0, max=140)]
    )
    submit = SubmitField("Submit")
