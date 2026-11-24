from django.contrib.auth.views import LogoutView
from django.urls import path

from . import dashboard_views as v

app_name = 'dashboard'

urlpatterns = [
    path('', v.OverviewView.as_view(), name='overview'),
    path('login/', v.DashboardLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
]