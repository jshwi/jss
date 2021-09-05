"""
app.forms
=========
"""
# pylint: disable=too-few-public-methods
from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    PasswordField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

from .models import User


class RegistrationForm(FlaskForm):
    """Form for registering a new user."""

    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Register")

    # noinspection PyMethodMayBeStatic
    def validate_username(  # pylint: disable=no-self-use
        self, username: StringField
    ) -> None:
        """WTForms invokes the pattern against the property.

        :param username:    Username will be validated for
                            ``validate_username``
        """
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Username is taken")

    # noinspection PyMethodMayBeStatic
    def validate_email(  # pylint: disable=no-self-use
        self, email: StringField
    ) -> None:
        """WTForms invokes the pattern against the property.

        :param email: Email will be validated for ``validate_email``
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
    """Form for blog posts."""

    title = StringField("Title", validators=[DataRequired()])
    body = TextAreaField(
        "Body",
        validators=[DataRequired()],
        render_kw={"rows": 24, "cols": 168},
    )
    submit = SubmitField("Submit")
