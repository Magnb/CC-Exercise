from app.config import Config
from app.custom_flask import CustomFlask
from app.repositories.influx_repo import setup_influxdb
from app.repositories.mqtt_repo import setup_mqtt


def create_app():
    app = CustomFlask(__name__)

    app.config.from_object(Config)

    # Initialize InfluxDB client
    setup_influxdb(app)

    # Initialize MQTT client
    setup_mqtt(app)

    # Register routes
    from app.api.routes import api_blueprint
    app.register_blueprint(api_blueprint)

    return app
