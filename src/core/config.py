import os

# InfluxDB configuration
#INFLUXDB_URL = os.getenv("INFLUXDB_URL", "0.0.0.0:8086")

# Use the Docker service name "influxdb" and default port 8086
INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://influxdb:8086")  # ✅ Correct setup

INFLUXDB_HOST = "influxdb"  # ✅ Correct inside Docker
INFLUXDB_PORT = 8086

INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "oNbS4DQvupHwZhvaZFYfADESfx84kKPHFtpZ659uie9IOAG87VkXadSqOG3tZsnqk2X_x8YZ87Sd4OA29lTXHA==")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "ENI")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "battery01")

# MQTT configuration
MQTT_BROKER = os.getenv("MQTT_BROKER", "mqtt-broker")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "battery/power")


class Config:
    MQTT_BROKER = "mqtt-broker"  # Your MQTT broker address
    MQTT_PORT = 1883           # MQTT port
    MQTT_TOPIC = "battery/power"  # Topic to subscribe to
    INFLUXDB_URL = "http://influxdb:8086"
    INFLUXDB_TOKEN = "oNbS4DQvupHwZhvaZFYfADESfx84kKPHFtpZ659uie9IOAG87VkXadSqOG3tZsnqk2X_x8YZ87Sd4OA29lTXHA=="
    INFLUXDB_ORG = "ENI"
    INFLUXDB_BUCKET = "battery1"
