import paho.mqtt.client as mqtt
import psycopg2
import psycopg2.pool
import json
import uuid
from datetime import datetime, timezone

MQTT_BROKER = "mosquitto"
current_topics = []

db_pool = psycopg2.pool.SimpleConnectionPool(
    1, 5,
    user="postgres",
    password="postgres",
    host="postgres",
    port="5432",
    database="postgres"
)

def update_subscriptions(client):
  try:
    conn = db_pool.getconn()
    cur = conn.cursor()
    cur.execute("""
      SELECT name
      FROM gateway_gateway g
    """)
    rows = cur.fetchall()
    conn.commit()
    cur.close()
    for row in rows:
      topic = f"{row[0]}/#"
      client.subscribe(topic,0)
      print(f"Subscribed to topic: {topic}")
  except Exception as e:
    print(f"Error reading database: {e}")
  finally:
    if conn:
      db_pool.putconn(conn)

def on_connect(client, userdata, flags, rc):
  print("Connected with result code " + str(rc))
  client.subscribe("mqtt/control/refresh", 2)
  update_subscriptions(client)
  

def on_message(client, userdata, msg):
  if msg.topic == 'mqtt/control/refresh':
    current_topics = update_subscriptions(client)
  else:
    payload = msg.payload.decode()
    topic = msg.topic
    print(f"Received message: {payload} from topic: {topic}")

    try:
      conn = db_pool.getconn()
      cur = conn.cursor()
      gateway, profile, device = topic.split("/")
      timestamp = datetime.now(timezone.utc)
      cur.execute("""
        SELECT d.profile_id pid, d.id
        FROM gateway_gateway g
        JOIN devices_device d
        ON d.gateway_id = g.id
        WHERE d.name = %s
        AND g.name = %s
      """, [device, gateway])
      row = cur.fetchone()
      device_id = row[1]
      profile_id = row[0]
      data = json.loads(payload)["readings"]
      for reading in data:
        cur.execute("""
          SELECT r.id
          FROM profiles_deviceresource r
          WHERE r.name = %s AND profile_id = %s
        """, [reading["resourceName"], profile_id])
        resource_id = cur.fetchone()[0]
        value = reading["value"]
        cur.execute(
          "INSERT INTO mqtt_data (value, timestamp, resource_id, device_id, uid) VALUES (%s, %s, %s, %s, %s)",
          (value, timestamp, resource_id, device_id, str(uuid.uuid4()))
        )
      conn.commit()
      cur.close()
    except Exception as e:
      print(f"Error saving to database: {e}")
    finally:
      if conn:
        db_pool.putconn(conn)
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, 1883, 60)
client.loop_forever()
