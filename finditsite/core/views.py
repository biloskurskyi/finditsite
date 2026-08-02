from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView


class TitleMixin:
    title = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        return context


class LandingView(TitleMixin, TemplateView):
    template_name = "core/landing.html"
    title = _("FindIt")
