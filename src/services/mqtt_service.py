import json
import os
import paho.mqtt.client as mqtt
import requests

MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "mqtt-broker")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", 1883))
FLASK_API_HOST = os.getenv("FLASK_API_HOST", "flask-app")
FLASK_API_PORT = os.getenv("FLASK_API_PORT", "5003")
WRITE_ENDPOINT = f"http://{FLASK_API_HOST}:{FLASK_API_PORT}/write"


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"✅ Connected to MQTT broker at {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}")
        client.subscribe("battery/power")  # Subscribe to relevant topic
        print("✅ Subscribed to topic: battery/power")
    else:
        print(f"❌ Failed to connect to MQTT broker, return code {rc}")


def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()

    print(f"📩 Received MQTT message on topic: {topic} -> {payload}")

    if topic == "battery/power":
        try:
            parsed = json.loads(payload)
            response = requests.post(WRITE_ENDPOINT, json=parsed)

            if response.status_code == 200:
                print(f"✅ Wrote to InfluxDB successfully")
            else:
                print(f"❌ Failed to post to InfluxDB: {response.text}")

        except (ValueError, json.JSONDecodeError) as e:
            print(f"❌ Invalid JSON format received: {e}")
        except Exception as e:
            print(f"❌ Error sending power data: {e}")


def start_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        print(f"🚀 Connecting MQTT service to {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}...")
        client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT)
        client.loop_forever()  # Keep the loop running
    except Exception as e:
        print(f"❌ Error connecting to MQTT broker: {e}")


if __name__ == "__main__":
    start_mqtt()


def setup_mqtt_publisher(app):
    """
    Initialize MQTT client for publishing messages.
    """
    MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "mqtt-broker")
    MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", 1883))

    # Create an MQTT client
    app.mqtt_client = mqtt.Client()

    try:
        print(f"✅ Connecting Flask to MQTT broker at {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}...")
        app.mqtt_client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT)
    except Exception as e:
        print(f"❌ MQTT Connection failed: {e}")