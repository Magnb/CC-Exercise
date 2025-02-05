import os
from flask.cli import load_dotenv

# Load environment variables from .env file (for secrets)
load_dotenv()


class Config:
    """Base Configuration Class"""

    # 🔷 MQTT Configuration
    MQTT_BROKER = os.getenv("MQTT_BROKER_HOST", "mqtt-broker")
    MQTT_PORT = int(os.getenv("MQTT_BROKER_PORT", 1883))
    MQTT_TOPIC = os.getenv("MQTT_TOPIC", "battery/charge")
    MQTT_TOPIC_DISCHARGE = os.getenv("MQTT_TOPIC", "battery/discharge")

    # 🔷 InfluxDB Configuration
    INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://influxdb:8086")
    INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "<secret>!!!")  # Never hardcode secrets!
    INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "ENI")
    INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "battery1")

    # 🔷 Flask API Configuration
    FLASK_API_HOST = os.getenv("FLASK_API_HOST", "flask-app")
    FLASK_API_PORT = os.getenv("FLASK_API_PORT", "5003")
    WRITE_ENDPOINT = f"http://{FLASK_API_HOST}:{FLASK_API_PORT}/write"

    @staticmethod
    def init_app(app):
        """Initialize Flask app with config values"""
        app.config.from_object(Config)
