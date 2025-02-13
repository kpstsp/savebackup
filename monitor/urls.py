from django.urls import path
from .views import site_create_view, site_update_view, site_list_view

urlpatterns = [
    path('', site_list_view, name='site_list'),
    path('site/create/', site_create_view, name='site_create'),
    path('site/<int:pk>/edit/', site_update_view, name='site_edit'),
]