import time
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests

# API endpoint to fetch data
#API_URL = "http://127.0.0.1:5003/read"
API_URL = "http://flask-app:5003/read"


# Function to fetch time series data from Flask API
@st.cache_data(ttl=30)  # Cache results for 30 seconds
def fetch_time_series():
    response = requests.get(API_URL)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch data: {response.text}")
        return []


# Function to create a Plotly time series chart
def plot_time_series(data, chart_type):
    df = pd.DataFrame(data)

    fig = go.Figure()

    if chart_type == "Line Chart":
        fig.add_trace(go.Scatter(
            x=df["time"], y=df["power"],
            mode="lines+markers",
            name="Power (kW)"
        ))
    elif chart_type == "Bar Chart":
        fig.add_trace(go.Bar(
            x=df["time"], y=df["power"],
            name="Power (kW)"
        ))

    fig.update_layout(
        title="⚡ Power Over Time",
        xaxis_title="Time",
        yaxis_title="Power (kW)",
        template="plotly_dark"
    )
    return fig


# Streamlit UI
st.title("📈 Power Monitoring Dashboard")

# Fetch & Display Data
data = fetch_time_series()
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
    st.sidebar.metric("🔼 Max Power", f"{df['power'].max()} kW")
    st.sidebar.metric("🔽 Min Power", f"{df['power'].min()} kW")
    st.sidebar.metric("⚡ Average Power", f"{df['power'].mean():.2f} kW")

    # Show raw data in an expandable table
    with st.expander("📊 View Raw Data"):
        st.dataframe(pd.DataFrame(data))

# Auto-refresh every 30 seconds (optional)
auto_refresh = st.sidebar.checkbox("⏳ Auto-Refresh Every 10s")
if auto_refresh:
    time.sleep(10)
    st.rerun()
