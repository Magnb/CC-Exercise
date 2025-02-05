import json
import paho.mqtt.client as mqtt
import requests
from src.core.config import Config


def on_connect(client, userdata, flags, rc, properties):
    """
    Handles connection to MQTT broker.
    Uses the new callback API version (v2).
    """
    if rc == 0:
        print(f"✅ Connected to MQTT broker at {Config.MQTT_BROKER}:{Config.MQTT_PORT}")

        # Subscribe to multiple topics
        try:
            client.subscribe([(Config.MQTT_TOPIC, 0), (Config.MQTT_TOPIC_DISCHARGE, 0)])
            print(f"✅ Subscribed to topics: {Config.MQTT_TOPIC}, {Config.MQTT_TOPIC_DISCHARGE}")
        except Exception as e:
            print(f"❌ Failed to subscribe to topics: {e}")

        print(f"✅ Subscribed to topics: {Config.MQTT_TOPIC}, {Config.MQTT_TOPIC_DISCHARGE}")
    else:
        print(f"❌ Failed to connect to MQTT broker, return code {rc}")


def on_message(client, userdata, msg):
    payload = msg.payload.decode()

    print(f"📩 Received MQTT message on topic: {msg.topic} -> {payload}")
    endpoint = ""
    if msg.topic == Config.MQTT_TOPIC:
        endpoint = Config.WRITE_CHARGE_ENDPOINT

    elif msg.topic == Config.MQTT_TOPIC_DISCHARGE:
        endpoint = Config.WRITE_DISCHARGE_ENDPOINT

    if not endpoint:
        print(f"❌ No endpoint defined for topic: {msg.topic}")
        return

    try:
        parsed = json.loads(payload)
        response = requests.post(endpoint, json=parsed)

        if response.status_code == 200:
            print(f"✅ Wrote to InfluxDB successfully")
        else:
            print(f"❌ Failed to post to InfluxDB: {response.text}")

    except (ValueError, json.JSONDecodeError) as e:
        print(f"❌ Invalid JSON format received: {e}")
    except Exception as e:
        print(f"❌ Error sending charge data: {e}")


def start_mqtt():
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
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



