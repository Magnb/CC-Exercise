import json
from datetime import datetime
from dateutil.parser import parse
from flask import Blueprint, request, jsonify, current_app
from flask_restx import Api, Resource, fields

from src.api.mqtt_publisher import mqtt_publish
from src.core.config import Config
from src.services.influx_service import read_battery_data, influx_write_charge, influx_write_discharge

api_blueprint = Blueprint("api", __name__)
api = Api(api_blueprint, title="Battery API", version="1.0", description="API for battery data management")

# Global variable to store the latest SOC value
latest_charge = {"charge": None, "unit": "kW", "timestamp": None}

# Swagger Models

charge_model = api.model("Charging", {
    "charge": fields.Integer(required=True, description="charge value"),
    "unit": fields.String(required=False, description="charge unit"),
    "timestamp": fields.String(required=False, description="Timestamp"),
})

discharge_model = api.model("Discharging", {
    "discharge": fields.Integer(required=True, description="charge value"),
    "unit": fields.String(required=False, description="charge unit"),
    "timestamp": fields.String(required=False, description="Timestamp"),
})


@api.route("/charge", methods=["POST"])
class Setcharge(Resource):
    @api.doc(description="Send charge command via MQTT publishing")
    @api.expect(api.model("chargeCommand", {
        "charge": fields.Float(required=True, description="charge value"),
        "unit": fields.String(required=False, description="Unit, defaults to kW")

    }))
    def post(self):
        data = request.json

        # Validate request data
        if "charge" not in data:
            return {"error": "Missing 'charge' field"}, 400

        charge = data["charge"]

        unit = "kW"
        timestamp = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
        if "unit" in data:
            unit = data["unit"]

        try:
            # Publish as a JSON object
            mqtt_message = {
                "charge": charge,
                "unit": unit,
                "timestamp": timestamp
            }

            mqtt_publish(
               # mqtt_client=current_app.mqtt_client,
                topic=Config.MQTT_TOPIC,
                command=json.dumps(mqtt_message)
            )

            print(f"Published charge: {mqtt_message} to {Config.MQTT_TOPIC}")
            return {"message": f"charge set to: {charge} {unit}"}, 200

        except Exception as e:
            return {"error": str(e)}, 500


@api.route("/discharge", methods=["POST"])
class SetDischarge(Resource):
    @api.doc(description="Send discharge command via MQTT publishing")
    @api.expect(api.model("dischargeCommand", {
        "discharge": fields.Float(required=True, description="discharge value"),
        "unit": fields.String(required=False, description="Unit, defaults to kW")

    }))
    def post(self):
        data = request.json

        # Validate request data
        if "discharge" not in data:
            return {"error": "Missing 'charge' field"}, 400

        discharge = data["discharge"]

        unit = "kW"
        timestamp = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
        if "unit" in data:
            unit = data["unit"]

        try:
            # Publish as a JSON object
            mqtt_message = {
                "discharge": discharge,
                "unit": unit,
                "timestamp": timestamp
            }

            mqtt_publish(
               # mqtt_client=current_app.mqtt_client,
                topic=Config.MQTT_TOPIC_DISCHARGE,
                command=json.dumps(mqtt_message)
            )

            print(f"Published charge: {mqtt_message} to {Config.MQTT_TOPIC_DISCHARGE}")
            return {"message": f"charge set to: {discharge} {unit}"}, 200

        except Exception as e:
            return {"error": str(e)}, 500


@api.route("/read")
class ReadBatteryData(Resource):
    @api.doc(description="Retrieve battery data from InfluxDB")
    @api.param("begin", "Start time for query (default: -1h)", required=False)
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
class WriteChargeValue(Resource):
    @api.expect(charge_model)
    @api.response(200, "Data written successfully")
    @api.response(400, "Invalid payload")
    def post(self):
        """Write battery charge data"""
        data = request.json
        if not data:
            return {"error": "Invalid payload"}, 400

        try:
            global latest_charge
            latest_charge["value"] = data["charge"]

            # If no timestamp is provided, take the current time in UTC and set milliseconds to 00
            if "timestamp" in data:
                parsed_timestamp = parse(data["timestamp"]).isoformat()
            else:
                now = datetime.utcnow().replace(microsecond=0)
                parsed_timestamp = now.isoformat() + "Z"  # Append "Z" for UTC indication

            latest_charge["timestamp"] = parsed_timestamp

            influx_write_charge(
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


@api.route("/writeDischarge")
class WriteDischargeValue(Resource):
    @api.expect(discharge_model)
    @api.response(200, "Data written successfully")
    @api.response(400, "Invalid payload")
    def post(self):
        """Write battery charge data"""
        data = request.json
        if not data:
            return {"error": "Invalid payload"}, 400

        try:
            # If no timestamp is provided, take the current time in UTC and set milliseconds to 00
            if "timestamp" in data:
                parsed_timestamp = parse(data["timestamp"]).isoformat()
            else:
                now = datetime.utcnow().replace(microsecond=0)
                parsed_timestamp = now.isoformat() + "Z"  # Append "Z" for UTC indication

            influx_write_discharge(
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


@api.route("/livedata")
class GetCurrentSOC(Resource):
    @api.doc(description="Retrieve the latest charging value")
    def get(self):
        """Get the latest SOC value"""
        return jsonify(latest_charge)
