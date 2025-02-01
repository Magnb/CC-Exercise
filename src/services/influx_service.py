from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from src.core.config import Config
from datetime import datetime


def setup_influxdb(app):
    """
    Initialize InfluxDB client with token and URL.
    Attach write_api and query_api to the Flask app.
    """
    app.influx_client = InfluxDBClient(
        url=Config.INFLUXDB_URL,
        token=Config.INFLUXDB_TOKEN,
        org=Config.INFLUXDB_ORG
    )
    app.write_api = app.influx_client.write_api(write_options=SYNCHRONOUS)
    app.query_api = app.influx_client.query_api()


def influx_write_battery_soc(write_api, bucket, org, data):
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
            .field("SOC", data["SOC"])
            .time(data.get("timestamp", datetime.utcnow().isoformat()))
        )
        write_api.write(bucket=bucket, org=org, record=point)

    except KeyError as e:
        raise KeyError(f"Missing key in payload: {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to write data: {str(e)}")


def influx_write_battery_data(write_api, bucket, org, data):
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
            .field("power", data["power"])
            #.field("target_discharge", data["target_discharge"])
            #.field("target_charge", data["target_charge"])
            .time(data.get("timestamp", datetime.utcnow().isoformat()))
        )
        write_api.write(bucket=bucket, org=org, record=point)

    except KeyError as e:
        raise KeyError(f"Missing key in payload: {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to write data: {str(e)}")


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
                    "power": record.get_value() if record.get_field() == "power" else None,
                    #"target_discharge": record.get_value() if record.get_field() == "target_discharge" else None,
                    #"target_charge": record.get_value() if record.get_field() == "target_charge" else None
                })
        return results
    except Exception as e:
        raise RuntimeError(f"Error reading data from InfluxDB: {str(e)}")