from django.views.generic import TemplateView

from django.shortcuts import render


class AboutPageView(TemplateView):
    """Returns about project page"""

    template_name = 'pages/about.html'

class RulesPageView(TemplateView):
    """Returns project rules pages"""

    template_name = 'pages/rules.html'


def page_not_found(request, exception=None):
    """Page not found"""

    return render(request, 'pages/404.html', status=404)


def csrf_failure(request, reason=''):
    """CSRF Failure"""

    return render(request, 'pages/403csrf.html', status=403)


def server_error(request):
    """Server Error"""

    return render(request, 'pages/500.html', status=500)