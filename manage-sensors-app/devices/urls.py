from django.urls import path
from . import views

urlpatterns = [
  path('', views.devices_list , name='devices-list'),
  path('create-device/', views.create_device, name= 'create-device'),
  path("<uuid:pk>/", views.device_detail, name="device-detail"),
  path('<uuid:pk>/delete/', views.DeviceDeleteView.as_view(), name='delete-device'),
  path('<uuid:pk>/edit/', views.edit_device, name='edit-device'),
]
