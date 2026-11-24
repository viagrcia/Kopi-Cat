from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('map/', views.cafe_map_view, name='map'),
    path('journal/', views.journal_view, name='journal'),
    path('journal/entry/new/', views.entry_save, name='entry_create'),
    path('journal/entry/<int:pk>/edit/', views.entry_save, name='entry_update'),
    path('journal/entry/<int:pk>/delete/', views.entry_delete, name='entry_delete'),
    path('journal/strip/<int:slot>/', views.strip_upload, name='strip_upload'),
    path('journal/strip/<int:slot>/clear/', views.strip_clear, name='strip_clear'),
    path('journal/stickers/add/', views.sticker_add, name='sticker_add'),
    path('journal/stickers/<int:pk>/move/', views.sticker_move, name='sticker_move'),
    path('journal/stickers/<int:pk>/delete/', views.sticker_delete, name='sticker_delete'),
    path('developer/', views.about_dev_view, name='about_dev'),
    path('login/', views.SiteLoginView.as_view(), name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
]