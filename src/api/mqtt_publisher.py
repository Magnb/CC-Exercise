import paho.mqtt.client as mqtt
from src.core.config import Config


def mqtt_publish(topic, command):
    """
    Publishes a message to the MQTT broker.
    This function creates a new connection per message to ensure that Flask does not
    maintain a persistent MQTT connection.
    """
    try:
        client = mqtt.Client()
        client.connect(Config.MQTT_BROKER, Config.MQTT_PORT)
        client.publish(topic, command)
        client.disconnect()  # Close connection after publishing
        print(f"✅ Published to {topic}: {command}")
    except Exception as e:
        print(f"❌ Failed to publish MQTT message: {e}")


