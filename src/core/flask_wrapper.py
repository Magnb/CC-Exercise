import paho.mqtt.client as mqtt
from flask import Flask
from influxdb_client import WriteApi, QueryApi
import os
import threading


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
        MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "mqtt-broker")
        MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", 1883))

        self.mqtt_client = mqtt.Client()

        def connect_mqtt():
            try:
                print(f"✅ Connecting Flask to MQTT broker at {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}...")
                self.mqtt_client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT)
                self.mqtt_client.loop_start()  # Start non-blocking loop
            except Exception as e:
                print(f"❌ MQTT Connection failed: {e}")

        # Run MQTT connection in a separate thread
        threading.Thread(target=connect_mqtt, daemon=True).start()
