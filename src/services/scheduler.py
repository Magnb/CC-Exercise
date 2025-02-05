import random
import time
import requests
from datetime import datetime
import threading

# API endpoint for writing charge data

WRITE_ENDPOINT = "flask-app:5003/setcharge"


def get_charge_command():
    """Fetch the latest charge value from MQTT or use the default."""
    while True:
        current_charge = random.randint(10, 20)
        print(f"🔄 New charge value to send: {current_charge}")

        return {
            "charge": current_charge,
            "unit": "kW"
        }


def generate_charge_value():
    """Generate an SOC value between the latest stored command."""
    command = get_charge_command()
    return command["charge"]


def send_charge_data():
    """Continuously writes charge data every full minute."""
    while True:
        # Get the current time and wait for the next full minute
        now = datetime.utcnow()
        sleep_time = 60 - now.second  # Wait until the next minute starts
        time.sleep(sleep_time)  # Pause execution

        # Generate an SOC value within the limits
        command = get_charge_command()

        # Create timestamp with minute precision
        timestamp = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

        # Prepare data payload
        data = {
            "charge": command["charge"],
            "unit": command["unit"],
            #"timestamp": timestamp
        }

        try:
            # Send request to write new charge data
            response = requests.post(WRITE_ENDPOINT, json=data)
            if response.status_code == 200:
                print(f"[{timestamp}] Sent charge value {command} successfully.")
            else:
                print(f"[{timestamp}] Failed to send charge value: {response.text}")
        except Exception as e:
            print(f"Error sending charge data: {e}")


# Start the SOC writer in a separate thread
soc_writer_thread = threading.Thread(target=send_charge_data, daemon=True)
soc_writer_thread.start()

# Prevent main thread from exiting
soc_writer_thread.join()  # This will keep the main script running
