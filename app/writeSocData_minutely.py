import time
import requests
import random
from datetime import datetime
import threading

# API endpoint for writing SOC data
WRITE_ENDPOINT = "http://127.0.0.1:5003/write"

# Global SOC limits (default values in case MQTT hasn't updated them yet)
soc_limits = {
    "upper": 100,  # Default upper limit
    "lower": 20    # Default lower limit
}


def get_latest_limits():
    """Fetch the latest SOC limits from MQTT or use defaults."""
    # Ensure this function gets the latest values safely
    return {
        "upper": soc_limits.get("upper", 100),  # Default to 100 if missing
        "lower": soc_limits.get("lower", 20)    # Default to 20 if missing
    }


def generate_soc():
    """Generate an SOC value between the latest stored limits."""
    limits = get_latest_limits()
    return int(random.uniform(limits["lower"], limits["upper"]))


def run_soc_writer():
    """Continuously writes SOC data every full minute."""
    while True:
        # Get the current time and wait for the next full minute
        now = datetime.utcnow()
        sleep_time = 60 - now.second  # Wait until the next minute starts
        time.sleep(sleep_time)  # Pause execution

        # Generate an SOC value within the limits
        soc_value = generate_soc()

        # Create timestamp with minute precision
        timestamp = datetime.utcnow().replace(second=0, microsecond=0).isoformat() + "Z"

        # Prepare data payload
        data = {
            "SOC": soc_value,
            "timestamp": timestamp
        }

        try:
            # Send request to write SOC data
            response = requests.post(WRITE_ENDPOINT, json=data)
            if response.status_code == 200:
                print(f"[{timestamp}] Sent SOC {soc_value} successfully.")
            else:
                print(f"[{timestamp}] Failed to send SOC: {response.text}")
        except Exception as e:
            print(f"Error sending SOC data: {e}")


# Start the SOC writer in a separate thread
soc_writer_thread = threading.Thread(target=run_soc_writer, daemon=True)
soc_writer_thread.start()

# Prevent main thread from exiting
soc_writer_thread.join()  # This will keep the main script running
