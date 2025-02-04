# Use a lightweight Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy only the MQTT service files
COPY src/services/mqtt_service.py /app/mqtt_service.py
COPY src/api/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV MQTT_BROKER_HOST=mqtt-broker
ENV MQTT_BROKER_PORT=1883
ENV FLASK_API_HOST=flask-app
ENV FLASK_API_PORT=5003

# Run the MQTT service
CMD ["python", "mqtt_service.py"]
