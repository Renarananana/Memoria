from django.db import models
from devices.models import Device
from profiles.models import DeviceResource
import uuid

# Create your models here.
class Data(models.Model):
  uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  device = models.ForeignKey(Device, on_delete=models.SET_NULL, null=True)
  resource = models.ForeignKey(DeviceResource, on_delete=models.SET_NULL, null=True)
  value = models.CharField()
  timestamp = models.DateTimeField(auto_now_add=True)