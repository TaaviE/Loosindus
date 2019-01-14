from flask_babelex import gettext as _
from flask_security.forms import StringField, Required, RegisterForm, ResetPasswordForm, SendConfirmationForm, \
    ForgotPasswordForm
from flask_wtf import RecaptchaField


class ExtendedRegisterForm(RegisterForm):
    username = StringField(_("Eesnimi"), [Required()])
    recaptcha = RecaptchaField("Captcha")


class ExtendedResetForm(ResetPasswordForm):
    recaptcha = RecaptchaField("Captcha")


class ExtendedConfirmationForm(SendConfirmationForm):
    recaptcha = RecaptchaField("Captcha")


class ExtendedForgotPasswordForm(ForgotPasswordForm):
    recaptcha = RecaptchaField("Captcha")
