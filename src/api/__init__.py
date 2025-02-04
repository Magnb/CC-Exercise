from src.core.config import Config
from src.core.influx_db_flask import InfluxDBFlaskApp
from src.services.influx_service import setup_influxdb
from src.services.mqtt_service import setup_mqtt_publisher


def create_app():
    app = InfluxDBFlaskApp(__name__)

    app.config.from_object(Config)

    # Initialize InfluxDB client
    setup_influxdb(app)

    # Initialize MQTT client
    setup_mqtt_publisher(app)

    # Register routes
    from src.api.routes import api_blueprint
    app.register_blueprint(api_blueprint)

    return app
