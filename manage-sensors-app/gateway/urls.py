from django.urls import path
from . import views

urlpatterns = [
  path('', views.gateway_list, name='gateways-list'),
  path("create-gateway/", views.create_gateway, name="create-gateway"),
  path("<int:pk>/delete-gateway/", views.GatewatDeleteView.as_view(), name="delete-gateway"),
  path("<int:pk>/", views.gateway_detail, name="gateway-detail"),
  path("<int:pk>/ping", views.gateway_ping, name="gateway-ping"),
  path("<int:pk>/edit", views.edit_gateway, name="edit-gateway"),
  path("<int:pk>/disable", views.disable_gateway, name="disable-gateway"),
  path("<int:pk>/activate", views.activate_gateway, name="activate-gateway"),
  path("<int:pk>/synch-profiles", views.synch_profiles, name="synch-profiles"),
  path("<int:pk>/synch-devices", views.synch_devices, name="synch-devices"),
  path("<int:pk>/update-profiles", views.update_gateway_profiles, name="update-profiles"),
  path("<int:pk>/add-profile", views.add_profile, name="add-profile"),
  path("<int:pk>/new-token", views.new_token, name="new-token"),
  path("sign-csr", views.sign_csr, name="sign-csr"),
]