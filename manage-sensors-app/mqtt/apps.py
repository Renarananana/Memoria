from django.apps import AppConfig
import os


class MqttConfig(AppConfig):
  default_auto_field = 'django.db.models.BigAutoField'
  name = 'mqtt'
  
  def ready(self):
    if os.environ.get('RUN_MAIN', None) != 'true':
      return  # Previene doble ejecución en runserver

    from .mqtt import start_mqtt
    #start_mqtt()
