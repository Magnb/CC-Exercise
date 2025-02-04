import os
import json
import paho.mqtt.client as mqtt

# Read environment variables
MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "mqtt-broker")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", 1883))

def mqtt_publish(topic, command):
    """
    Publishes a message to the MQTT broker.
    This function creates a new connection per message to ensure that Flask does not
    maintain a persistent MQTT connection.
    """
    try:
        client = mqtt.Client()
        client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT)
        client.publish(topic, command)
        client.disconnect()  # Close connection after publishing
        print(f"✅ Published to {topic}: {command}")
    except Exception as e:
        print(f"❌ Failed to publish MQTT message: {e}")
