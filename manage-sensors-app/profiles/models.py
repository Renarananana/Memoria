from django.db import models
from django.core.exceptions import ValidationError
import enum

#     "profile": {
#       "labels": [
#         "modbus"
#       ],
#       "deviceResources": [
#         {
#           "name": "SwitchButton",
#           "description": "Switch On/Off.",
#           "properties": {
#             "valueType": "String",
#             "readWrite": "RW",
#             "defaultValue": "On",
#             "units": "On/Off"
#           }
#         }
#       ],
#       "deviceCommands": [
#         {
#           "name": "Switch",
#           "readWrite": "RW",
#           "resourceOperations": [
#             {
#               "deviceResource": "SwitchButton",
#               "DefaultValue": "false"
#             }
#           ]
#         }
#       ]
#     }
# Create your models here.
class Labels(models.Model):
  name = models.CharField(max_length=100)
  
  def __str__(self):
    return self.name

class DeviceProfile(models.Model):
  name = models.CharField(max_length=100)
  manufacturer = models.CharField()
  model = models.CharField()
  labels = models.ManyToManyField(Labels)
  description = models.CharField()
  
  def clean(self):
    if self.pk and not self.resources.exists():
      raise ValidationError("A Device profile require at least one Resource")
  
  def __str__(self):
    return self.name

class ValueTypes(enum.Enum):
  Uint8 = "Uint8"
  Uint16 = "Uint16"
  Uint32 = "Uint32"
  Uint64 = "Uint64"
  Int8 = "Int8"
  Int16 = "Int16"
  Int32 = "Int32"
  Int64 = "Int64"
  Float32 = "Float32"
  Float64 = "Float64"
  Bool = "Bool"
  String = "String"
  Binary = "Binary"
  Object = "Object"
  Uint8Array = "Uint8Array"
  Uint16Array = "Uint16Array"
  Uint32Array = "Uint32Array"
  Uint64Array = "Uint64Array"
  Int8Array = "Int8Array"
  Int16Array = "Int16Array"
  Int32Array = "Int32Array"
  Int64Array = "Int64Array"
  Float32Array = "Float32Array"
  Float64Array = "Float64Array"
  BoolArray = "BoolArray"

class ReadWrite(models.TextChoices):
  READ = "R", "Read"
  WRITE = "W", "Write"
  READWRITE = "RW", "Read and Write"

class ResourceProperties(models.Model):
  VALUETYPES = [(e.name, e.value) for e in ValueTypes]
  valueType = models.CharField(max_length=20, choices=VALUETYPES)
  readWrite = models.CharField(max_length=10, choices=ReadWrite.choices)

class DeviceResource(models.Model):
  name = models.CharField(max_length=100)
  description = models.CharField()
  properties = models.OneToOneField(ResourceProperties, on_delete=models.CASCADE)
  profile = models.ForeignKey(DeviceProfile, on_delete=models.CASCADE, related_name='resources')


class DeviceCommand(models.Model):
  name = models.CharField(max_length=100)
  readWrite = models.CharField(max_length=10, choices=ReadWrite.choices)
  profile = models.ForeignKey(DeviceProfile, on_delete=models.CASCADE, related_name='commands')
  
  def clean(self):
    if self.pk and not self.operations.exists():
      raise ValidationError("A Device Command require at least one operation")

class DeviceOperation(models.Model):
  defaultValue = models.CharField()
  command = models.ForeignKey(DeviceCommand, on_delete=models.CASCADE, related_name='operations')
  resource = models.ForeignKey(DeviceResource, on_delete=models.CASCADE)