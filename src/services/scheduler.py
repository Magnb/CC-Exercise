import random
import time
import requests
from datetime import datetime
import threading

# API endpoint for writing power data
WRITE_ENDPOINT = "http://127.0.0.1:5003/setPower"


def get_power_command():
    """Fetch the latest power value from MQTT or use the default."""
    while True:
        current_power = random.randint(10, 20)
        print(f"🔄 New power value to send: {current_power}")

        return {
            "power": current_power,
            "unit": "kW"
        }


def generate_power_value():
    """Generate an SOC value between the latest stored command."""
    command = get_power_command()
    return command["power"]


def send_power_data():
    """Continuously writes power data every full minute."""
    while True:
        # Get the current time and wait for the next full minute
        now = datetime.utcnow()
        sleep_time = 60 - now.second  # Wait until the next minute starts
        time.sleep(sleep_time)  # Pause execution

        # Generate an SOC value within the limits
        command = get_power_command()

        # Create timestamp with minute precision
        timestamp = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

        # Prepare data payload
        data = {
            "power": command["power"],
            "unit": command["unit"],
            #"timestamp": timestamp
        }

        try:
            # Send request to write new power data
            response = requests.post(WRITE_ENDPOINT, json=data)
            if response.status_code == 200:
                print(f"[{timestamp}] Sent power value {command} successfully.")
            else:
                print(f"[{timestamp}] Failed to send power value: {response.text}")
        except Exception as e:
            print(f"Error sending power data: {e}")


# Start the SOC writer in a separate thread
soc_writer_thread = threading.Thread(target=send_power_data, daemon=True)
soc_writer_thread.start()

# Prevent main thread from exiting
soc_writer_thread.join()  # This will keep the main script running
