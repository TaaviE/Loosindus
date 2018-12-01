from flask_security.forms import StringField, Required, RegisterForm, ResetPasswordForm, SendConfirmationForm, \
    ForgotPasswordForm
from flask_wtf import RecaptchaField


class ExtendedRegisterForm(RegisterForm):
    username = StringField("Eesnimi", [Required()])  # TODO: Translate I think
    recaptcha = RecaptchaField("Captcha")


class ExtendedResetForm(ResetPasswordForm):
    recaptcha = RecaptchaField("Captcha")


class ExtendedConfirmationForm(SendConfirmationForm):
    recaptcha = RecaptchaField("Captcha")


class ExtendedForgotPasswordForm(ForgotPasswordForm):
    recaptcha = RecaptchaField("Captcha")
