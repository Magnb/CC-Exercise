import json
import paho.mqtt.client as mqtt
import requests
from src.core.config import Config


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"✅ Connected to MQTT broker at {Config.MQTT_BROKER}:{Config.MQTT_PORT}")
        client.subscribe(Config.MQTT_TOPIC)  # Subscribe to relevant topic
        print("✅ Subscribed to topic: battery/charge")
    else:
        print(f"❌ Failed to connect to MQTT broker, return code {rc}")


def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()

    print(f"📩 Received MQTT message on topic: {topic} -> {payload}")

    if topic == Config.MQTT_TOPIC:
        try:
            parsed = json.loads(payload)
            response = requests.post(Config.WRITE_ENDPOINT, json=parsed)

            if response.status_code == 200:
                print(f"✅ Wrote to InfluxDB successfully")
            else:
                print(f"❌ Failed to post to InfluxDB: {response.text}")

        except (ValueError, json.JSONDecodeError) as e:
            print(f"❌ Invalid JSON format received: {e}")
        except Exception as e:
            print(f"❌ Error sending charge data: {e}")


def start_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        print(f"🚀 Connecting MQTT service to {Config.MQTT_BROKER}:{Config.MQTT_PORT}...")
        client.connect(Config.MQTT_BROKER, Config.MQTT_PORT)
        client.loop_forever()  # Keep the loop running
    except Exception as e:
        print(f"❌ Error connecting to MQTT broker: {e}")


if __name__ == "__main__":
    start_mqtt()



