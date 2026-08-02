from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, TemplateView

from core.views import TitleMixin
from recognition.forms import ResultUploadForm
from recognition.selectors import latest_result_for, recent_result_dates
from recognition.services.recognition import create_result


class ModeWorkspaceMixin(TitleMixin):
    @property
    def title(self):
        return _("FindIt - %(mode)s") % {"mode": self.kwargs["mode"].label}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mode = self.kwargs["mode"]
        context["mode"] = mode
        if self.request.user.is_authenticated:
            context["latest_result"] = latest_result_for(self.request.user, mode)
            context["result_dates"] = recent_result_dates(self.request.user, mode)
        return context


class ModeDetailView(ModeWorkspaceMixin, TemplateView):
    def get_template_names(self):
        if self.request.user.is_authenticated:
            return ["recognition/mode_detail.html"]
        return ["recognition/mode_teaser.html"]

    def get_context_data(self, **kwargs):
        return super().get_context_data(form=ResultUploadForm(), **kwargs)


class ResultCreateView(LoginRequiredMixin, ModeWorkspaceMixin, FormView):
    template_name = "recognition/mode_detail.html"
    form_class = ResultUploadForm

    def form_valid(self, form):
        try:
            create_result(
                self.request.user,
                self.kwargs["mode"],
                form.cleaned_data["template_image"],
                form.cleaned_data["reference_image"],
            )
        except ValidationError as error:
            form.add_error(None, error)
            return self.form_invalid(form)
        return self.render_to_response(self.get_context_data(form=ResultUploadForm()))
