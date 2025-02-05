# Battery Charging

## POC for Real-Time Battery Monitoring and Control:
Monitor the Charging values of a battery.
Log and visualize historical data for insights and diagnostics.
Build using Flask microservices for flexibility and scalability.
Use MQTT for lightweight communication, enabling integration with IoT devices.

Time Series Visualization:
Leverage Plotly for interactive time-series graphs of SOC and power usage.
Provide users with actionable insights into their energy usage and market performance.

## Database Design
Use InfluxDB to store time-series data, including:

Battery Metrics:
Charge/Discharge rate (kW)
Timestamp

## MQTT Use Case
Use MQTT for real-time communication:

Publish:
Commands for charge/discharge rates - e.g. Discharge 50kW
Subscribe:
Updates on market prices or battery state changes.

## Visualization
Use Plotly to create dashboards with the following graphs:

SOC Over Time: Visualize the battery's charge level (kWh).
Charge/Discharge Trends: Show when and how the battery is charged/discharged.

### Optional Optimization Feature
Market Data:
Forecasted intra-day electricity prices
Timestamps

Incorporate a simple optimization model for battery operations:

Market Optimization (Optional but adds value):
Use forecasted intra-day prices to optimize when to charge or discharge the battery for cost savings or profit maximization.
Generate optimal charge/discharge schedules.

Use forecasted intra-day prices to calculate:
When to charge (low prices).
When to discharge (high prices).
Constraints:
Max/min SOC limits.
Battery efficiency (roundtrip loss).
Maximum charge/discharge rates.
Generate an hourly schedule and display it on the dashboard.

Visualize Market Prices vs. Battery Behavior: Correlate price changes with battery usage to validate the optimization.


curl -X POST http://127.0.0.1:5000/write -H "Content-Type: application/json" \
-d '{"SOC": 700, "target_discharge": 50, "target_charge": 100, "timestamp": "2025-01-16T10:00:00Z"}'

curl "http://127.0.0.1:5003/read?begin=2025-01-16T09:00:00Z&end=2025-01-16T11:00:00Z"

curl -X POST http://127.0.0.1:5000/mqtt/publish -H "Content-Type: application/json" \
-d '{"command": "DISCHARGE 50kW"}'

curl -X POST http://127.0.0.1:5003/write -H "Content-Type: application/json" \
-d '{"SOC": 500, "target_discharge": 0, "target_charge": 400, "timestamp": "2025-01-14T10:00:00Z"}'
