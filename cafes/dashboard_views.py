from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView

from .models import ActivityLog, Cafe


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Only logged-in staff accounts can open dashboard pages."""
    login_url = reverse_lazy('dashboard:login')

    def test_func(self):
        return self.request.user.is_staff


class StaffAuthForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_staff:
            raise ValidationError('This area is for the site owner only.', code='not_staff')


class DashboardLoginView(LoginView):
    template_name = 'dashboard/login.html'
    authentication_form = StaffAuthForm
    redirect_authenticated_user = True

    def get_default_redirect_url(self):
        return reverse('dashboard:overview')


class OverviewView(StaffRequiredMixin, TemplateView):
    template_name = 'dashboard/overview.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        User = get_user_model()
        incomplete = Cafe.objects.filter(
            Q(image='') | Q(image__isnull=True) | Q(rating__isnull=True) | Q(hours='')
        ).order_by('name')
        ctx.update({
            'active': 'overview',
            'cafe_count': Cafe.objects.count(),
            'user_count': User.objects.filter(is_staff=False).count(),
            'attention_count': incomplete.count(),
            'log_count': ActivityLog.objects.count(),
            'attention': incomplete[:6],
            'recent': ActivityLog.objects.select_related('user')[:8],
        })
        return ctx