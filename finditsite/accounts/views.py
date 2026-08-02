from django.contrib.auth import views as auth_views
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic.edit import CreateView

from accounts.forms import LoginForm, RegistrationForm
from core.views import TitleMixin


class RegistrationView(TitleMixin, SuccessMessageMixin, CreateView):
    model = User
    form_class = RegistrationForm
    template_name = "accounts/registration.html"
    success_url = reverse_lazy("accounts:login")
    success_message = _("Registration is successfully done!")
    title = _("FindIt - Registration")


class LoginView(TitleMixin, auth_views.LoginView):
    template_name = "accounts/login.html"
    form_class = LoginForm
    title = _("FindIt - Log in")
