import logging

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.generic.edit import FormView

from cms.utils import timezone
from .forms import TimetravelForm
from .utils import reset_timetravel_date


class TimetravelView(FormView):
    form_class = TimetravelForm
    template_name = 'cms_timetravel/form.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(TimetravelView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        response = super(TimetravelView, self).get(request, *args, **kwargs)
        if 'clear' in self.request.GET:
            logging.debug('Clearing session keys timetravel_date and auto_redirect.')
            return self._clear()
        return response

    def get_context_data(self, **kwargs):
        context = super(TimetravelView, self).get_context_data(**kwargs)
        context['title'] = _('Timetravel')
        context['timetravel_date'] = self.request.session.get('timetravel_date', None)
        return context

    def get_initial(self):
        initial = super(TimetravelView, self).get_initial()
        initial['timetravel_date'] = self.request.session.get('timetravel_date', timezone.now())
        initial['auto_redirect'] = self.request.session.get('auto_redirect', True)
        return initial

    def form_valid(self, form):
        self.request.session['timetravel_date'] = form.cleaned_data['timetravel_date']
        self.request.session['auto_redirect'] = form.cleaned_data['auto_redirect']
        return super(TimetravelView, self).form_valid(form)

    def get_success_url(self):
        if self.request.session.get('auto_redirect', False):
            return reverse('pages-root')  # CMS Root-page
        return reverse('cms_timetravel:timetravel')

    def _clear(self):
        try:
            del self.request.session['timetravel_date']
            reset_timetravel_date()
        except KeyError:
            logging.debug("Unable to delete key for timetravelling.")
        return HttpResponseRedirect(reverse('cms_timetravel:timetravel'))
