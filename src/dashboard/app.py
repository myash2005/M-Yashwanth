import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import time
from datetime import datetime
from src.utils.alerts import send_discord_alert

st.set_page_config(page_title="PdM Dashboard", layout="wide")

st.title("🏭 AI-Driven Predictive Maintenance Dashboard")

# Sidebar
st.sidebar.header("Configuration")
api_url = st.sidebar.text_input("API URL", "http://localhost:8000/predict")
discord_webhook = st.sidebar.text_input("Discord Webhook URL (Optional)", "")
refresh_rate = st.sidebar.slider("Refresh Rate (s)", 1, 10, 2)

# Load data for simulation
@st.cache_data
def load_sim_data():
    df = pd.read_csv('data/ai4i2020.csv')
    df.columns = [c.replace('[', '').replace(']', '').replace('<', '') for c in df.columns]
    return df

data = load_sim_data()

if 'index' not in st.session_state:
    st.session_state.index = 0
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame()

# Simulation loop controls
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("Start Simulation"):
        st.session_state.running = True
with col2:
    if st.button("Stop Simulation"):
        st.session_state.running = False

# Function to get color for schematic
def get_health_color(value, threshold_yellow, threshold_red, inverse=False):
    if not inverse:
        if value >= threshold_red: return "red"
        if value >= threshold_yellow: return "yellow"
        return "green"
    else:
        if value <= threshold_red: return "red"
        if value <= threshold_yellow: return "yellow"
        return "green"

def create_schematic(sensors, health_score):
    fig = go.Figure()

    # Motor (based on Speed/Torque)
    motor_color = "green"
    if sensors['Torque Nm'] > 60 or sensors['Rotational speed rpm'] > 2500 or sensors['Rotational speed rpm'] < 1300:
        motor_color = "red"
    elif sensors['Torque Nm'] > 50 or sensors['Rotational speed rpm'] > 2000:
        motor_color = "yellow"

    # Tool (based on Tool Wear)
    tool_color = get_health_color(sensors['Tool wear min'], 150, 200)
    if health_score > 0.8: tool_color = "red"
    elif health_score > 0.5 and tool_color == "green": tool_color = "yellow"

    # Cooling (based on Temp)
    cooling_color = get_health_color(sensors['Air temperature K'], 303, 305)

    # Drawing the machine
    # Base
    fig.add_shape(type="rect", x0=1, y0=1, x1=9, y1=2, line_color="Black", fillcolor="lightgrey")

    # Motor block
    fig.add_shape(type="rect", x0=2, y0=2, x1=4, y1=5, line_color="Black", fillcolor=motor_color)
    fig.add_annotation(x=3, y=3.5, text="Motor", showarrow=False)

    # Cooling unit
    fig.add_shape(type="rect", x0=4.5, y0=2, x1=6.5, y1=4, line_color="Black", fillcolor=cooling_color)
    fig.add_annotation(x=5.5, y=3, text="Cooling", showarrow=False)

    # Tool / Spindle
    fig.add_shape(type="circle", x0=7, y0=3, x1=8.5, y1=5, line_color="Black", fillcolor=tool_color)
    fig.add_annotation(x=7.75, y=4, text="Tool", showarrow=False)

    fig.update_xaxes(visible=False, range=[0, 10])
    fig.update_yaxes(visible=False, range=[0, 6])
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=20, b=20), title="2D Machine Health Schematic")

    return fig

# Dashboard Layout
placeholder = st.empty()

if 'running' in st.session_state and st.session_state.running:
    row = data.iloc[st.session_state.index]

    # Call API
    payload = {
        "Type": row['Type'],
        "Air_temperature": float(row['Air temperature K']),
        "Process_temperature": float(row['Process temperature K']),
        "Rotational_speed": float(row['Rotational speed rpm']),
        "Torque": float(row['Torque Nm']),
        "Tool_wear": float(row['Tool wear min'])
    }

    try:
        resp = requests.post(api_url, json=payload).json()
        prob = resp['failure_probability']
        rul = resp['estimated_rul']
    except:
        prob = 0.0
        rul = 0.0

    # Update History
    new_row = row.copy()
    new_row['Failure Prob'] = prob
    new_row['Timestamp'] = datetime.now()
    st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([new_row])]).tail(50)

    # Alerting
    if prob > 0.8:
        send_discord_alert(discord_webhook, row['Type'], prob, row)

    # Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Failure Probability", f"{prob:.2%}", delta=None, delta_color="inverse")
    m2.metric("Est. RUL", f"{rul:.1f} min")
    m3.metric("Tool Wear", f"{row['Tool wear min']} min")
    m4.metric("Torque", f"{row['Torque Nm']} Nm")

    # Schematic and Charts
    c1, c2 = st.columns([1, 1])
    with c1:
        st.plotly_chart(create_schematic(row, prob), use_container_width=True, key=f"schematic_{st.session_state.index}")

    with c2:
        # Sensor Trend
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(x=st.session_state.history['Timestamp'], y=st.session_state.history['Air temperature K'], name="Air Temp"))
        fig_trend.add_trace(go.Scatter(x=st.session_state.history['Timestamp'], y=st.session_state.history['Process temperature K'], name="Process Temp"))
        fig_trend.update_layout(title="Temperature Trends", height=300)
        st.plotly_chart(fig_trend, use_container_width=True, key=f"temp_trend_{st.session_state.index}")

    # Lower Charts
    c3, c4 = st.columns(2)
    with c3:
        fig_speed = go.Figure()
        fig_speed.add_trace(go.Scatter(x=st.session_state.history['Timestamp'], y=st.session_state.history['Rotational speed rpm'], name="RPM", line=dict(color='royalblue')))
        fig_speed.update_layout(title="Rotational Speed", height=250)
        st.plotly_chart(fig_speed, use_container_width=True, key=f"speed_trend_{st.session_state.index}")
    with c4:
        fig_prob = go.Figure()
        fig_prob.add_trace(go.Scatter(x=st.session_state.history['Timestamp'], y=st.session_state.history['Failure Prob'], name="Prob", fill='tozeroy'))
        fig_prob.update_layout(title="Failure Probability Trend", height=250)
        st.plotly_chart(fig_prob, use_container_width=True, key=f"prob_trend_{st.session_state.index}")

    st.session_state.index = (st.session_state.index + 1) % len(data)
    time.sleep(refresh_rate)
    st.rerun()
else:
    st.info("Click 'Start Simulation' to begin monitoring.")
