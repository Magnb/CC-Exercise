import json
from collections import deque

import paho.mqtt.client as mqtt
import requests

# Buffer for storing recent MQTT messages
MESSAGE_BUFFER_SIZE = 100
message_buffer = deque(maxlen=MESSAGE_BUFFER_SIZE)

# API endpoint for writing power data
WRITE_ENDPOINT = "http://127.0.0.1:5003/write"


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
        # Use userdata to get the MQTT_TOPIC
        mqtt_topic = userdata.get("MQTT_TOPIC", "default/topic")
        client.subscribe(mqtt_topic)
        print(f"Subscribed to topic: {mqtt_topic}")
    else:
        print(f"Failed to connect, return code {rc}")


def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()

    print(f"📩 Received MQTT message on topic: {topic} -> {payload}")

    if topic == "battery/power":
        try:
            parsed = json.loads(payload)
            # Send request to write new power data
            response = requests.post(WRITE_ENDPOINT, json=parsed)
            if response.status_code == 200:
                print(f"Wrote to InfluxDB successfully")
            else:
                print(f"Failed to post to InfluxDB: {response.text}")
        except (ValueError, json.JSONDecodeError) as e:
            print(f"❌ Invalid JSON format received: {e}")
        except Exception as e:
            print(f"Error sending power data: {e}")


def mqtt_publish(mqtt_client, topic, command):
    if not command:
        raise ValueError("Command cannot be empty")
    try:
        mqtt_client.publish(topic, command)
    except Exception as e:
        raise RuntimeError(f"Failed to publish MQTT command: {str(e)}")


def setup_mqtt(app):
    # Create the MQTT client
    client = mqtt.Client()

    # Pass app configuration as userdata to the client
    client.user_data_set({
        "MQTT_TOPIC": "battery/power"
    })

    # Set callbacks
    client.on_connect = on_connect
    client.on_message = on_message

    # Attach the MQTT client to the app instance
    app.mqtt_client = client

    # Connect to the MQTT broker
    client.connect(app.config.get("MQTT_BROKER", "localhost"), app.config.get("MQTT_PORT", 1883))
    client.subscribe("battery/power")
    client.loop_start()

