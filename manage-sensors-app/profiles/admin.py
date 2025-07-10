from django.contrib import admin
from .models import Labels, DeviceResource, ResourceProperties, DeviceProfile, DeviceOperation, DeviceCommand

# Register your models here.
admin.site.register(Labels)
admin.site.register(DeviceResource)
admin.site.register(ResourceProperties)
admin.site.register(DeviceProfile)
admin.site.register(DeviceOperation)
admin.site.register(DeviceCommand)