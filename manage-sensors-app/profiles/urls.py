from django.urls import path
from . import views

urlpatterns = [
  path('', views.profiles_list , name='profiles-list'),
  path('create-profile', views.create_profile , name='create-profile'),
  path("<int:pk>/", views.device_profile_detail, name="device-profile-detail"),
  path('<int:pk>/delete/', views.DeviceProfileDeleteView.as_view(), name='device-profile-delete'),
  path('<int:pk>/edit-profile', views.edit_profile, name='edit-profile'), 

]
