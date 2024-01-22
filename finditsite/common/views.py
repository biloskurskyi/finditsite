from django.views.generic import TemplateView


class TitleMixin:
    title = None

    def get_context_data(self, **kwargs):
        context = super(TitleMixin, self).get_context_data()
        context['title'] = self.title
        return context


class BaseView(TitleMixin, TemplateView):
    title = "FindIt"
