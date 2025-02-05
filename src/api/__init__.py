from src.core.config import Config
from src.core.flask_wrapper import FlaskWrapper


def create_app():
    app = FlaskWrapper(__name__)
    app.config.from_object(Config)

    # Initialize InfluxDB client
    from src.services.influx_service import setup_influxdb
    setup_influxdb(app)

    # Import routes *after* setting up the app to avoid circular imports
    from src.api.routes import api_blueprint
    app.register_blueprint(api_blueprint)

    return app
