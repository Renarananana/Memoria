from django.urls import path
from .views import data_plot_view, command_view

urlpatterns = [
  path('plot/<uuid:device_pk>/<int:resource_pk>/', data_plot_view, name='plot'),
  path('command/<uuid:device_pk>/<int:command_pk>/', command_view, name='command'),
]