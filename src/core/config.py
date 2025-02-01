import os

# InfluxDB configuration
INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "KdN1PAAWzJL5BEHvShsntw7zcfc5IyOUdAZBlf1jjkHV_DCHCU7TslsARgPQl4Z2KGWebp0SzuC6jpKxAgvbrg==")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "ENI")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "battery01")

# MQTT configuration
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "battery/power")


class Config:
    MQTT_BROKER = "localhost"  # Your MQTT broker address
    MQTT_PORT = 1883           # MQTT port
    MQTT_TOPIC = "battery/power"  # Topic to subscribe to
    INFLUXDB_URL = "http://localhost:8086"
    INFLUXDB_TOKEN = "KdN1PAAWzJL5BEHvShsntw7zcfc5IyOUdAZBlf1jjkHV_DCHCU7TslsARgPQl4Z2KGWebp0SzuC6jpKxAgvbrg=="
    INFLUXDB_ORG = "ENI"
    INFLUXDB_BUCKET = "battery1"