from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class RegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["username", "email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs["placeholder"] = _("Enter username..")
        self.fields["email"].widget.attrs["placeholder"] = _("Enter email..")
        self.fields["password1"].widget.attrs["placeholder"] = _("Enter password..")
        self.fields["password2"].widget.attrs["placeholder"] = _("Re-enter password..")


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs["placeholder"] = _("Enter username..")
        self.fields["password"].widget.attrs["placeholder"] = _("Enter password..")
