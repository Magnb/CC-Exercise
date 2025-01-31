import json
from collections import deque

import paho.mqtt.client as mqtt

# Buffer for storing recent MQTT messages
MESSAGE_BUFFER_SIZE = 100
message_buffer = deque(maxlen=MESSAGE_BUFFER_SIZE)

# Global variables for SOC limits
soc_limits = {
    "upper": 100,  # Default upper limit
    "lower": 20    # Default lower limit
}


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
    """Handles incoming MQTT messages and updates SOC limits."""
    topic = msg.topic
    payload = msg.payload.decode()

    print(f"Received MQTT message: {topic} -> {payload}")

    if topic == "SOC_limits":
        try:
            # Parse JSON message
            data = json.loads(payload)
            if "upper_limit" in data:
                soc_limits["upper"] = int(data["upper_limit"])
                print(f"Updated upper SOC limit: {soc_limits['upper']}")

            if "lower_limit" in data:
                soc_limits["lower"] = int(data["lower_limit"])
                print(f"Updated lower SOC limit: {soc_limits['lower']}")

        except (ValueError, json.JSONDecodeError) as e:
            print(f"Invalid JSON format received: {e}")


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
        "MQTT_TOPIC": app.config.get("MQTT_TOPIC", "default/topic")
    })

    # Set callbacks
    client.on_connect = on_connect
    client.on_message = on_message

    # Attach the MQTT client to the app instance
    app.mqtt_client = client

    # Connect to the MQTT broker
    client.connect(app.config.get("MQTT_BROKER", "localhost"), app.config.get("MQTT_PORT", 1883))
    client.loop_start()
