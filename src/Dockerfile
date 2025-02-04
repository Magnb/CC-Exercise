# Use an official Python image
FROM python:3.9-slim

# Set working directory inside the container
WORKDIR /app

# Copy and install dependencies
COPY dashboard/dashboard-requirements.txt .
RUN pip install --no-cache-dir -r dashboard-requirements.txt

# Copy the entire dashboard directory
COPY dashboard /app/dashboard

# Expose Streamlit’s default port
EXPOSE 8501

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run Streamlit app
CMD ["streamlit", "run", "dashboard/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
