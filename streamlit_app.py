import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set Page Config
st.set_page_config(
    page_title='UNILORIN Park Condition',
    page_icon='🚌',
    layout='wide'
)

# --- DATA PREPARATION ---
@st.cache_data
def load_park_data():
    # 1. Queue Inflow & Residue (From Image Data)
    queue_data = {
        "Time": ["07:30", "07:45", "08:00", "08:15", "08:30", "08:45", "09:00", "09:15", "09:30", "09:45", "10:00", "10:15", "10:30"],
        "Inflow": [16, 132, 130, 200, 178, 192, 183, 144, 161, 185, 209, 273, 252],
        "Residue": [0, 5, 8, 15, 66, 56, 105, 133, 150, 210, 182, 150, 125] # Estimated from text/images
    }
    
    # 2. Vehicle Capacities
    capacities = {
        "Korope": 8, "12-Seater": 12, "14-Seater": 14, 
        "CNG Bus": 15, "18-Seater": 18, "Medium Bus": 25, "Marcopolo": 60
    }
    
    return pd.DataFrame(queue_data), capacities

df_queue, caps = load_park_data()

# --- UI HEADER ---
st.title("🚌 UNILORIN Park Condition Monitor")
st.markdown(f"""
    **Assignment Goal:** Providing students with hints on park conditions every hour.  
    *Status based on data collected from 07:20 AM to 11:00 AM.*
""")

# --- KPI METRICS ---
latest_residue = df_queue['Residue'].iloc[-1]
status = "CRITICAL" if latest_residue > 150 else "BUSY" if latest_residue > 50 else "CLEAR"
status_color = "red" if status == "CRITICAL" else "orange" if status == "BUSY" else "green"

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Current Queue Residue", f"{latest_residue} People")
with col2:
    st.subheader(f"Status: :{status_color}[{status}]")
with col3:
    st.metric("Peak Inflow Rate", f"{df_queue['Inflow'].max()} students/15m")

st.divider()

# --- VISUALIZATION 1: QUEUE TRENDS ---
st.header("📈 Queue Accumulation vs. Inflow")
fig_trend = go.Figure()
fig_trend.add_trace(go.Scatter(x=df_queue['Time'], y=df_queue['Inflow'], name='Joining Queue', line=dict(color='#3498db', width=3)))
fig_trend.add_trace(go.Bar(x=df_queue['Time'], y=df_queue['Residue'], name='People Left Behind', marker_color='#e74c3c', opacity=0.6))

fig_trend.update_layout(
    xaxis_title="Time of Day",
    yaxis_title="Number of People",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    hovermode="x unified"
)
st.plotly_chart(fig_trend, use_container_width=True)

# --- VISUALIZATION 2: VEHICLE MIX & LOGISTICS ---
col_left, col_right = st.columns([1, 1])

with col_left:
    st.header("🚐 Fleet Mix Capacity")
    fleet_df = pd.DataFrame({
        "Vehicle": caps.keys(),
        "Capacity": caps.values()
    })
    fig_fleet = px.pie(fleet_df, values='Capacity', names='Vehicle', title='Passenger Capacity per Vehicle Type', hole=0.4)
    st.plotly_chart(fig_fleet, use_container_width=True)

with col_right:
    st.header("⏱️ Operational Hints")
    st.info("""
    **Observations:**
    - **Fastest Loading:** CNG and Korope (1-2 mins).
    - **Heavy Lifters:** Marcopolos (Average load time: 18 mins).
    - **Bottleneck Warning:** Between 09:30 AM and 10:15 AM, the residue peaks above 200. Suggest using alternative transport or arriving earlier.
    """)
    
    # Simple search widget for students
    st.subheader("Check My Hour")
    check_time = st.selectbox("Select your travel time:", df_queue['Time'])
    selected_row = df_queue[df_queue['Time'] == check_time].iloc[0]
    st.write(f"At {check_time}, expect a backlog of approximately **{selected_row['Residue']} people**.")

# --- FOOTER ---
st.caption("Data Source: Student Group Observation Logs | University of Ilorin Park Project")
