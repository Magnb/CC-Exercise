import paho.mqtt.client as mqtt
from flask import Flask
from influxdb_client import WriteApi, QueryApi
import threading
from src.core.config import Config


class FlaskWrapper(Flask):
    write_api: WriteApi
    query_api: QueryApi
    mqtt_client: mqtt.Client  # Add MQTT client as an attribute

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_mqtt()

    def setup_mqtt(self):
        """
        Initialize MQTT client for publishing messages.
        """

        self.mqtt_client = mqtt.Client()

        def connect_mqtt():
            try:
                print(f"✅ Connecting Flask to MQTT broker at {Config.MQTT_BROKER}:{Config.MQTT_PORT}...")
                self.mqtt_client.connect(Config.MQTT_BROKER, Config.MQTT_PORT)
                self.mqtt_client.loop_start()  # Start non-blocking loop
            except Exception as e:
                print(f"❌ MQTT Connection failed: {e}")

        # Run MQTT connection in a separate thread
        threading.Thread(target=connect_mqtt, daemon=True).start()
