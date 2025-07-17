from django.db import models
from profiles.models import DeviceProfile
from gateway.models import Gateway
import uuid

# Create your models here.
# [
#   {
#     "apiVersion": "v3",
#     "device": {
#       "name": "my-custom-device-4",
#       "description": "MQTT device",
#       "adminState": "UNLOCKED",
#       "operatingState": "UP",
#       "labels": [
#         "MQTT",
#         "test"
#       ],
#       "serviceName": "device-mqtt",
#       "profileName": "my-custom-device-profile",
#       "protocols": {
#         "mqtt": {
#             "CommandTopic": "command/my-custom-device-4"
#         }
#       }
#     }
#   }
# ]
class Labels(models.Model):
  name = models.CharField(max_length=100)
  
  def __str__(self):
    return self.name

class AdminStates(models.TextChoices):
  UNLOCKED = "UNLOCKED", "Unlocked"
  LOCKED = "LOCKED", "Locked"
  
class OperatingStates(models.TextChoices):
  UP = "UP", "Up"
  DOWN = "DOWN", "Down"
  UNKNOWN = "UNKNOWN", "Unknown"

class Device(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4)
  name = models.CharField(max_length=100)
  description = models.CharField()
  admin_state = models.CharField( 
    max_length=10,
    choices= AdminStates.choices,
    default= AdminStates.UNLOCKED
    )
  operating_state = models.CharField( 
    max_length=10,
    choices= OperatingStates.choices,
    default= OperatingStates.UP
    )
  labels = models.ManyToManyField(Labels)
  profile = models.ForeignKey(DeviceProfile, on_delete=models.CASCADE)
  gateway = models.ForeignKey(Gateway, on_delete=models.SET_NULL, null=True)
  
  def __str__(self):
    return self.name
  
