from django.db import models
from django.utils import timezone
from utils.http_helpers import ping
from profiles.models import DeviceProfile
from cryptography.fernet import Fernet
from django.conf import settings
import secrets



class GatewayType(models.TextChoices):
  EDGEX = "EDGEX", 'EdgeX'
  SIMPLE = "SIMPLE", "Simple"
  CUSTOM = "CUSTOM", "Custom"


class Status(models.TextChoices):
  ACTIVE = "ACTIVE", 'Active'
  OFFLINE = "OFFLINE", "Offline"  
  DISABLED = "DISABLED", "Disabled"

class Gateway(models.Model):
  name = models.CharField(max_length=100)
  description = models.CharField()
  ip_address = models.CharField()
  api_port = models.IntegerField(default=443)
  gateway_type = models.CharField(
    max_length=10,
    choices=GatewayType.choices
  )
  status = models.CharField(
    max_length=10,
    choices=Status.choices
  )
  last_seen = models.DateTimeField(null=True, blank=True)
  profiles = models.ManyToManyField(DeviceProfile, through='GatewayProfiles')
  username = models.CharField(max_length=100, null=True, blank=True)
  password = models.BinaryField(null=True, blank=True)
  token = models.BinaryField(null=True, blank=True)
  
  def set_password(self, raw_password):
    if raw_password:  # Solo cifra si no es vacío
      f = Fernet(settings.ENCRYPTION_KEY)
      self.password = f.encrypt(raw_password.encode())
      print(self.password)

  def get_password(self):
    if self.password:
      f = Fernet(settings.ENCRYPTION_KEY)
      return f.decrypt(bytes(self.password)).decode()
    return None
  
  def create_token(self):
    token = secrets.token_hex(32)
    f = Fernet(settings.ENCRYPTION_KEY)
    self.token = f.encrypt(token.encode())
    self.save()
    return token

  def get_token(self):
    if self.token:
      f = Fernet(settings.ENCRYPTION_KEY)
      return f.decrypt(bytes(self.token)).decode()
    return None
  
  def check_online(self):
    try:
      if ping(self):
        return True
      else:
        return False
    except Exception as e:
      print(e)
      return False
  
  def disable(self):
    self.status = Status.DISABLED
    self.save()
    
  def activate(self):
    self.status = Status.ACTIVE
    self.update_status()

  def update_status(self):
    if self.status == Status.DISABLED:
      return
    if self.check_online():
      self.status = Status.ACTIVE
      self.last_seen = timezone.now()
    else:
      self.status = Status.OFFLINE
    self.save()
  def __str__(self):
    return self.name


class GatewayProfiles(models.Model):
  uid = models.UUIDField()
  gateway = models.ForeignKey(Gateway, on_delete=models.CASCADE)
  profile = models.ForeignKey(DeviceProfile, on_delete=models.CASCADE)