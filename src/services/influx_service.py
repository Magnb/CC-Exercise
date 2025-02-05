from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from src.core.config import Config
from datetime import datetime


def setup_influxdb(app):
    """
    Initialize InfluxDB client with token and URL.
    Attach write_api and query_api to the Flask app.
    """
    print(f"Connecting to InfluxDB at {Config.INFLUXDB_URL} with token length {len(Config.INFLUXDB_TOKEN)}")

    app.influx_client = InfluxDBClient(
        url=Config.INFLUXDB_URL,
        token=Config.INFLUXDB_TOKEN,
        org=Config.INFLUXDB_ORG
    )
    app.write_api = app.influx_client.write_api(write_options=SYNCHRONOUS)
    app.query_api = app.influx_client.query_api()


def read_battery_data(query_api, bucket, begin=None, end=None):
    """
    Retrieve battery data from InfluxDB.

    Args:
        query_api: InfluxDB Query API instance.
        bucket: Name of the InfluxDB bucket.
        begin: Start time (optional).
        end: End time (optional).

    Returns:
        List of dictionaries representing the queried data.
    """
    if begin and end:
        query = f'from(bucket: "{bucket}") |> range(start: {begin}, stop: {end}) |> filter(fn: (r) => r._measurement == "battery_data")'
    else:
        query = f'from(bucket: "{bucket}") |> range(start: -1h) |> filter(fn: (r) => r._measurement == "battery_data")'

    try:
        tables = query_api.query(query)
        results = []
        for table in tables:
            for record in table.records:
                results.append({
                    "time": record.get_time().isoformat(),
                    "charge": record.get_value() if record.get_field() == "charge" else None,
                    "discharge": record.get_value() if record.get_field() == "discharge" else None,
                })
        return results
    except Exception as e:
        raise RuntimeError(f"Error reading data from InfluxDB: {str(e)}")


def influx_write_charge(write_api, bucket, org, data):
    """
    Write battery data to InfluxDB.

    Args:
        write_api: InfluxDB Write API instance.
        bucket: Name of the InfluxDB bucket.
        org: InfluxDB organization name.
        data: Dictionary containing the data to write.
    """
    if not data:
        raise ValueError("Invalid payload: data cannot be empty")

    try:
        point = (
            Point("battery_data")
            .field("charge", data["charge"])
            .time(data.get("timestamp", datetime.utcnow().isoformat()))
        )
        write_api.write(bucket=bucket, org=org, record=point)

    except KeyError as e:
        raise KeyError(f"Missing key in payload: {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to write data: {str(e)}")


def influx_write_discharge(write_api, bucket, org, data):
    """
    Write battery data to InfluxDB.

    Args:
        write_api: InfluxDB Write API instance.
        bucket: Name of the InfluxDB bucket.
        org: InfluxDB organization name.
        data: Dictionary containing the data to write.
    """
    if not data:
        raise ValueError("Invalid payload: data cannot be empty")

    try:
        point = (
            Point("battery_data")
            .field("discharge", data["discharge"])
            .time(data.get("timestamp", datetime.utcnow().isoformat()))
        )
        write_api.write(bucket=bucket, org=org, record=point)

    except KeyError as e:
        raise KeyError(f"Missing key in payload: {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to write data: {str(e)}")

