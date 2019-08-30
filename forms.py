from flask_babelex import gettext as _
from flask_security.forms import StringField, RegisterForm, ResetPasswordForm, SendConfirmationForm, \
    ForgotPasswordForm
from flask_wtf import RecaptchaField
from wtforms.validators import DataRequired


class ExtendedRegisterForm(RegisterForm):
    """
    Adds first name and captcha to the registration form
    """
    first_name = StringField(_("First name"), [DataRequired()])
    recaptcha = RecaptchaField("Captcha")


class ExtendedResetForm(ResetPasswordForm):
    """
    Adds captcha to the password reset form
    """
    recaptcha = RecaptchaField("Captcha")


class ExtendedConfirmationForm(SendConfirmationForm):
    """
    Adds captcha to the confirm account form
    """
    recaptcha = RecaptchaField("Captcha")


class ExtendedForgotPasswordForm(ForgotPasswordForm):
    """
    Adds captcha to forgot password column
    """
    recaptcha = RecaptchaField("Captcha")
