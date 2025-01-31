import json
from datetime import datetime
from dateutil.parser import parse
from flask import Blueprint, request, jsonify, current_app
from flask_restx import Api, Resource, fields
from app.config import Config
from app.repositories.influx_repo import influx_write_battery_data, read_battery_data
from app.repositories.mqtt_repo import mqtt_publish, message_buffer

api_blueprint = Blueprint("api", __name__)
api = Api(api_blueprint, title="Battery API", version="1.0", description="API for battery data management")

# Global variable to store the latest SOC value
latest_soc = {"value": None, "timestamp": None}

# Swagger Models
soc_model = api.model("SOC", {
    "SOC": fields.Integer(required=True, description="State of Charge value"),
    "timestamp": fields.String(required=False, description="Timestamp of the SOC reading"),
})

message_model = api.model("Message", {
    "message": fields.String(description="Response message"),
})


# READ BATTERY DATA WITH TIME INTERVALS
@api.route("/read")
class ReadBatteryData(Resource):
    @api.doc(description="Retrieve battery data from InfluxDB")
    @api.param("begin", "Start time for query (default: -14h)", required=False)
    @api.param("end", "End time for query (default: now())", required=False)
    def get(self):
        """Fetch battery data based on time range"""
        begin = request.args.get("begin") or "-14h"
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
    @api.expect(soc_model)
    @api.response(200, "Data written successfully", message_model)
    @api.response(400, "Invalid payload")
    def post(self):
        """Write battery SOC data"""
        data = request.json
        if not data:
            return {"error": "Invalid payload"}, 400

        try:
            global latest_soc
            latest_soc["value"] = data["SOC"]

            # If no timestamp is provided, take the current time in UTC and set seconds & milliseconds to 00
            if "timestamp" in data:
                parsed_timestamp = parse(data["timestamp"]).isoformat()
            else:
                now = datetime.utcnow().replace(second=0, microsecond=0)  # Set seconds and microseconds to 00
                parsed_timestamp = now.isoformat() + "Z"  # Append "Z" for UTC indication

            latest_soc["timestamp"] = parsed_timestamp

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
        return jsonify(latest_soc)


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


@api.route("/setSOClimits", methods=["POST"])
class SetSOCLimits(Resource):
    @api.doc(description="Set the upper and lower SOC limit via MQTT")
    @api.expect(api.model("SOCLimits", {
        "upper_limit": fields.Float(required=True, description="Upper SOC limit value"),
        "lower_limit": fields.Float(required=True, description="Lower SOC limit value")
    }))
    def post(self):
        """Set both upper and lower SOC limits and publish them via MQTT"""
        data = request.json

        # Validate request data
        if "upper_limit" not in data or "lower_limit" not in data:
            return {"error": "Missing 'upper_limit' or 'lower_limit' field"}, 400

        upper_limit = data["upper_limit"]
        lower_limit = data["lower_limit"]
        mqtt_topic = "battery/SOC_limits"  # Hardcoded MQTT topic for limits

        try:
            # Publish both limits as a JSON object
            mqtt_message = {
                "upper_limit": upper_limit,
                "lower_limit": lower_limit
            }

            mqtt_publish(
                mqtt_client=current_app.mqtt_client,
                topic=mqtt_topic,
                command=json.dumps(mqtt_message)
            )

            print(f"Published SOC limits: {mqtt_message} to {mqtt_topic}")
            return {"message": f"SOC limits set: Upper = {upper_limit}, Lower = {lower_limit}"}, 200

        except Exception as e:
            return {"error": str(e)}, 500

