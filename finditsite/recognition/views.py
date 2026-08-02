from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from core.views import TitleMixin
from recognition.selectors import latest_result_for, recent_result_dates


class ModeDetailView(TitleMixin, TemplateView):
    @property
    def title(self):
        return _("FindIt - %(mode)s") % {"mode": self.kwargs["mode"].label}

    def get_template_names(self):
        if self.request.user.is_authenticated:
            return ["recognition/mode_detail.html"]
        return ["recognition/mode_teaser.html"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mode = self.kwargs["mode"]
        context["mode"] = mode
        if self.request.user.is_authenticated:
            context["latest_result"] = latest_result_for(self.request.user, mode)
            context["result_dates"] = recent_result_dates(self.request.user, mode)
        return context
