import paho.mqtt.client as mqtt
from django.conf import settings
from .models import Data
from devices.models import Device
from profiles.models import DeviceResource
import json



def on_connect(mqtt_client, userdata, flags, rc):
  if rc == 0:
    print('Connected successfully')
    mqtt_client.subscribe('edgex/events/device/device-mqtt/#')
  else:
    print('Bad connection. Code:', rc)


def on_message(mqtt_client, userdata, msg):
  payload = json.loads(msg.payload.decode())["payload"]
  data_recv = payload['event']["readings"][0]
  resource = DeviceResource.objects.get(name = data_recv["resourceName"])
  device = Device.objects.get(name = data_recv["deviceName"])
  Data.objects.create(
    device = device,
    resource = resource,
    value = data_recv["value"],
    valueType = data_recv["valueType"]
  )

def start_mqtt():
  client = mqtt.Client()
  client.on_connect = on_connect
  client.on_message = on_message
  client.username_pw_set(settings.MQTT_USER, settings.MQTT_PASSWORD)
  client.connect(
    host=settings.MQTT_SERVER,
    port=settings.MQTT_PORT,
    keepalive=settings.MQTT_KEEPALIVE
  )

  client.loop_start()
