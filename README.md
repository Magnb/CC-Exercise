# Battery Management Microservices Application
* This is a demo application for learning purposes trying out Python Flask with Streamlit *

## 🚀 Overview
This microservices-based application manages battery charge and discharge data using **Flask, MQTT, InfluxDB, and Streamlit**. It provides:
- **Battery API (Flask)** for managing charge/discharge values via **MQTT** and storing them in **InfluxDB**.
- **MQTT Service** for publishing battery charge/discharge data.
- **InfluxDB** for storing historical battery data.
- **Streamlit Dashboard** for real-time monitoring.

---
## 📌 Architecture
### **🔹 Components & Technologies**
- **Flask API**: Manages battery charge/discharge commands & stores data in InfluxDB.
- **MQTT Broker (Eclipse Mosquitto)**: Handles message communication.
- **InfluxDB**: Stores battery charge & discharge history.
- **Streamlit Dashboard**: Visualizes real-time data.
- **Docker & Docker Compose**: Containerized setup.

---
## 🏗️ Setup Instructions

### **🔹 Prerequisites**
Ensure you have the following installed:
- Docker & Docker Compose
- Python 3.x (for local development)

### **🔹 Start the Application (Dockerized Setup)**
```sh
docker-compose up -d --build
```

### **🔹 Start the Application (Manual Setup Without Docker)**
1. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```
2. Start the **MQTT broker (Mosquitto)**:
    ```sh
    mosquitto -v
    ```
3. Start the **Flask API**:
    ```sh
    python src/api/main.py
    ```
4. Start the **Streamlit Dashboard**:
    ```sh
    streamlit run src/dashboard/app.py
    ```

---
## 📡 API Endpoints (Flask Battery API)
| **Endpoint** | **Method** | **Description** |
|-------------|-----------|----------------|
| `/charge` | `POST` | Publish charge data via MQTT |
| `/discharge` | `POST` | Publish discharge data via MQTT |
| `/writeCharge` | `POST` | Store charge data in InfluxDB |
| `/writeDischarge` | `POST` | Store discharge data in InfluxDB |
| `/read` | `GET` | Retrieve battery data from InfluxDB |
| `/livedata` | `GET` | Fetch the latest charge/discharge values |

### **🔹 Example API Usage**
```sh
curl -X POST http://localhost:5003/charge -H "Content-Type: application/json" -d '{"charge": 10, "unit": "kW"}'
```
```sh
curl -X GET http://localhost:5003/livedata
```

---
## 📊 Streamlit Dashboard (Live Monitoring)
1. Access the dashboard at:
    ```sh
    http://localhost:8501
    ```
2. Displays real-time charge & discharge values from `/livedata`.

---
## ⚡ MQTT Topics
| **Topic** | **Description** |
|-----------|----------------|
| `battery/charge` | Publishes charge data via MQTT |
| `battery/discharge` | Publishes discharge data via MQTT |

---
## 🔄 Restarting a Single Service
```sh
docker-compose restart flask-app  # Restart Flask API
```
```sh
docker-compose restart mqtt-service  # Restart MQTT Service
```

---
## 🛠️ Troubleshooting
### **🔹 Check Logs**
```sh
docker logs flask-app  # View API logs
```
```sh
docker logs mqtt-service  # View MQTT logs
```
```sh
docker logs influxdb  # View InfluxDB logs
```
### **🔹 Verify Docker Containers Are Running**
```sh
docker ps
```

---

## 👨‍💻 Authors & Contributors
- **Magdalena Breitenauer**
