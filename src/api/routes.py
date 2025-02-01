import json
from datetime import datetime
from dateutil.parser import parse
from flask import Blueprint, request, jsonify, current_app
from flask_restx import Api, Resource, fields
from src import Config
from src import influx_write_battery_data, read_battery_data
from src import mqtt_publish, message_buffer

api_blueprint = Blueprint("api", __name__)
api = Api(api_blueprint, title="Battery API", version="1.0", description="API for battery data management")

# Global variable to store the latest SOC value
latest_power = {"power": None, "unit": None, "timestamp": None}

# Swagger Models
soc_model = api.model("SOC", {
    "SOC": fields.Integer(required=True, description="State of Charge value"),
    "timestamp": fields.String(required=False, description="Timestamp of the SOC reading"),
})

power_model = api.model("SOC", {
    "power": fields.Integer(required=True, description="Power value"),
    "unit": fields.String(required=False, description="Power unit"),
    "timestamp": fields.String(required=False, description="Timestamp"),
})

message_model = api.model("Message", {
    "message": fields.String(description="Response message"),
})


@api.route("/setPower", methods=["POST"])
class SetPower(Resource):
    @api.doc(description="Send power command via MQTT publishing")
    @api.expect(api.model("PowerCommand", {
        "power": fields.Float(required=True, description="Power value"),
        "unit": fields.String(required=False, description="Unit, defaults to kW")

    }))
    def post(self):
        data = request.json

        # Validate request data
        if "power" not in data:
            return {"error": "Missing 'power' field"}, 400

        power = data["power"]
        mqtt_topic = "battery/power"  # Hardcoded MQTT topic for power values

        unit = "kW"
        timestamp = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
        if "unit" in data:
            unit = data["unit"]

        try:
            # Publish as a JSON object
            mqtt_message = {
                "power": power,
                "unit": unit,
                "timestamp": timestamp
            }

            mqtt_publish(
                mqtt_client=current_app.mqtt_client,
                topic=mqtt_topic,
                command=json.dumps(mqtt_message)
            )

            print(f"Published power: {mqtt_message} to {mqtt_topic}")
            return {"message": f"Power set to: {power} {unit}"}, 200

        except Exception as e:
            return {"error": str(e)}, 500


# READ BATTERY DATA WITH TIME INTERVALS
@api.route("/read")
class ReadBatteryData(Resource):
    @api.doc(description="Retrieve battery data from InfluxDB")
    @api.param("begin", "Start time for query (default: -14h)", required=False)
    @api.param("end", "End time for query (default: now())", required=False)
    def get(self):
        """Fetch battery data based on time range"""
        begin = request.args.get("begin") or "-1h"
        end = request.args.get("end") or "now()"
        try:
            results = read_battery_data(
                query_api=current_app.query_api,
                bucket=Config.INFLUXDB_BUCKET,
                begin=begin,
                end=end
            )
            return jsonify(results)
        except RuntimeError as e:
            return {"error": str(e)}, 500


@api.route("/write")
class WriteBatteryData(Resource):
    @api.expect(power_model)
    @api.response(200, "Data written successfully", message_model)
    @api.response(400, "Invalid payload")
    def post(self):
        """Write battery power data"""
        data = request.json
        if not data:
            return {"error": "Invalid payload"}, 400

        try:
            global latest_power
            latest_power["value"] = data["power"]

            # If no timestamp is provided, take the current time in UTC and set seconds & milliseconds to 00
            if "timestamp" in data:
                parsed_timestamp = parse(data["timestamp"]).isoformat()
            else:
                now = datetime.utcnow().replace(second=0, microsecond=0)  # Set seconds and microseconds to 00
                parsed_timestamp = now.isoformat() + "Z"  # Append "Z" for UTC indication

            latest_power["timestamp"] = parsed_timestamp

            #mqtt_publish(
              #  mqtt_client=current_app.mqtt_client,
              #  topic=current_app.config["MQTT_TOPIC"],
              #  command=data["SOC"]
            #)

            influx_write_battery_data(
                write_api=current_app.write_api,
                bucket=Config.INFLUXDB_BUCKET,
                org=Config.INFLUXDB_ORG,
                data={**data, "timestamp": parsed_timestamp}
            )

            return {"message": "Data written successfully"}, 200
        except KeyError as e:
            return {"error": f"Missing key: {e}"}, 400
        except ValueError as e:
            return {"error": str(e)}, 400
        except RuntimeError as e:
            return {"error": str(e)}, 500



@api.route("/messages")
class GetMessages(Resource):
    @api.doc(description="Retrieve recent MQTT messages")
    def get(self):
        """Get recent MQTT messages"""
        return jsonify(list(message_buffer))


@api.route("/current-soc")
class GetCurrentSOC(Resource):
    @api.doc(description="Retrieve the latest SOC value")
    def get(self):
        """Get the latest SOC value"""
        return jsonify(latest_power)


@api.route("/timeseries")
class GetSOCTimeseries(Resource):
    @api.doc(description="Retrieve SOC time series data from InfluxDB")
    def get(self):
        """Fetch SOC time series for the last 24 hours"""
        try:
            data = read_battery_data(
                query_api=current_app.query_api,
                bucket=Config.INFLUXDB_BUCKET,
                begin="-24h",
                end="now()"
            )
            return jsonify(data)
        except RuntimeError as e:
            return {"error": str(e)}, 500


