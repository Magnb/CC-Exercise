import os
import threading
import paho.mqtt.client as mqtt
from src.core.config import Config
from src.core.flask_wrapper import FlaskWrapper


def setup_mqtt_publisher(app):
    """
    Initialize MQTT client for publishing messages.
    """
    MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "mqtt-broker")
    MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", 1883))

    app.mqtt_client = mqtt.Client()

    def connect_mqtt():
        try:
            print(f"✅ Connecting Flask to MQTT broker at {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}...")
            app.mqtt_client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT)
            app.mqtt_client.loop_start()  # Start MQTT in the background
        except Exception as e:
            print(f"❌ MQTT Connection failed: {e}")

    # Start MQTT connection in a separate thread
    threading.Thread(target=connect_mqtt, daemon=True).start()


def create_app():
    app = FlaskWrapper(__name__)  # ✅ Now MQTT is initialized inside the class
    app.config.from_object(Config)

    # Initialize InfluxDB client
    from src.services.influx_service import setup_influxdb
    setup_influxdb(app)

    # Import routes *after* setting up the app to avoid circular imports
    from src.api.routes import api_blueprint
    app.register_blueprint(api_blueprint)

    return app