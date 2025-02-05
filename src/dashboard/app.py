import time
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests

API_URL_READ = "http://flask-app:5003/read"
API_URL_LIVE = "http://flask-app:5003/livedata"


# Function to fetch time series data from Flask API
@st.cache_data(ttl=30)  # Cache results for 30 seconds
def fetch_time_series():
    response = requests.get(API_URL_READ)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch data: {response.text}")
        return []


@st.cache_data(ttl=30)  # Cache for 5 seconds
def fetch_live_data():
    """
    Fetch the latest live charge and discharge values from the API.
    """
    try:
        response = requests.get(API_URL_LIVE)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch data: {response.text}")
            return {"charge": None, "discharge": None, "unit": "kW", "timestamp": None}
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return {"charge": None, "discharge": None, "unit": "kW", "timestamp": None}


# Function to create a Plotly time series chart
def plot_time_series(data, chart_type):
    df = pd.DataFrame(data)

    fig = go.Figure()

    if chart_type == "Line Chart":
        fig.add_trace(go.Scatter(
            x=df["time"], y=df["charge"],
            mode="lines+markers",
            name="Charging (kW)"
        ))
        fig.add_trace(go.Scatter(
            x=df["time"], y=df["discharge"],
            mode="lines+markers",
            name="Discharging (kW)"
        ))
    elif chart_type == "Bar Chart":
        fig.add_trace(go.Bar(
            x=df["time"], y=df["charge"],
            name="Charging (kW)"
        ))
        fig.add_trace(go.Bar(
            x=df["time"], y=df["discharge"],
            name="Discharging (kW)"
        ))

    fig.update_layout(
        title="⚡ Charging Over Time",
        xaxis_title="Time",
        yaxis_title="Charging (kW)",
        template="plotly_dark"
    )
    return fig


# Streamlit UI
st.title("📈 Battery Charging Monitoring Dashboard")

# Create placeholders for live data
charge_metric = st.sidebar.empty()
discharge_metric = st.sidebar.empty()

# Fetch & Display Data
data = fetch_time_series()
livedata = fetch_live_data()

if data:
    df = pd.DataFrame(data)
    df["time"] = pd.to_datetime(df["time"])  # Convert to datetime

    # Sidebar Filters
    st.sidebar.header("⚙️ Filters")

    # Chart Type Selector
    chart_type = st.sidebar.radio("📊 Select Chart Type", ["Line Chart", "Bar Chart"])

    fig = plot_time_series(df, chart_type)
    st.plotly_chart(fig, use_container_width=True)

    # Summary Statistics
    st.sidebar.subheader("📊 Summary Statistics")

    st.sidebar.metric("🔼 Max charge", f"{df['charge'].max()} kW")
    st.sidebar.metric("🔽 Min charge", f"{df['charge'].min()} kW")
    st.sidebar.metric("⚡ Average charge", f"{df['charge'].mean():.2f} kW")

    st.sidebar.metric("🔼 Max discharge", f"{df['discharge'].max()} kW")
    st.sidebar.metric("🔽 Min discharge", f"{df['discharge'].min()} kW")
    st.sidebar.metric("⚡ Average discharge", f"{df['discharge'].mean():.2f} kW")

    # Show raw data in an expandable table
    with st.expander("📊 View Raw Data"):
        st.dataframe(pd.DataFrame(data))

# Auto-refresh historic data every 30 seconds (optional)
auto_refresh = st.sidebar.checkbox("⏳ Auto-Refresh Every 10s")
if auto_refresh:
    time.sleep(10)
    st.rerun()

# Live data loop (refreshes every 5 seconds)
while True:
    data = fetch_live_data()

    # Extract values safely (avoid NoneType errors)
    charge_value = data.get("charge", 0)
    discharge_value = data.get("discharge", 0)
    unit = data.get("unit", "kW")

    # ✅ Display dynamic metrics
    charge_metric.metric("Last charge value", f"⚡ {charge_value} {unit}")
    discharge_metric.metric("Last discharge value", f"⚡ {discharge_value} {unit}")

    # Wait before fetching new data
    time.sleep(30)  # Adjust update interval as needed


