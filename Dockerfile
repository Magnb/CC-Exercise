# Use an official lightweight Python image
FROM python:3.9-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements file first (Leverages Docker caching)
COPY src/api/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application source code
COPY src /app/src

# Expose Flask API port
EXPOSE 5003

# Set environment variables
ENV FLASK_APP=src/api/main.py
ENV FLASK_ENV=development
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Run Flask app
CMD ["python", "src/api/main.py"]
