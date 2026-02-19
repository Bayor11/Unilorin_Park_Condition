import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="University of Ilorin Park Condition",
    page_icon="🚌",
    layout="wide"
)

# --- DATA AGGREGATION ---
# Incorporating all shared datasets: Volume counts, Inflow/Residue, and Vehicle Logistics
@st.cache_data
def get_processed_data():
    # 1. Queue Dynamics (Inflow and Residue)
    queue_data = {
        "Time": ["07:30", "07:45", "08:00", "08:15", "08:30", "08:45", "09:00", "09:15", "09:30", "09:45", "10:00", "10:15", "10:30", "10:45"],
        "Students_Joining": [16, 132, 130, 200, 178, 192, 183, 144, 161, 185, 209, 273, 252, 125],
        "Residue": [0, 5, 8, 15, 66, 56, 105, 133, 150, 210, 182, 160, 140, 110]
    }
    df_queue = pd.DataFrame(queue_data)
    
    # 2. Vehicle Capacity Reference
    # Based on: 8=korope, 18=18 pass, 14=14 pass, 15=CNG, 12=12 pass, Marcopolo=~60
    vehicle_caps = {
        "Korope (8)": 8,
        "12-Passenger": 12,
        "14-Passenger": 14,
        "CNG Bus (15)": 15,
        "18-Passenger": 18,
        "Medium Bus": 25,
        "Marcopolo": 60
    }
    
    return df_queue, vehicle_caps

df_queue, vehicle_caps = get_processed_data()

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER SECTION ---
st.title("🚌 University of Ilorin Park Condition")
st.markdown("### Software for Probable Park Condition Hints")
st.info("This tool provides insights into passenger volume and queuing conditions to help students and staff plan their movements.")

# --- SECTION 1: LIVE STATUS & HINTS ---
# Identifying the current/latest state from the data
latest_idx = len(df_queue) - 1
current_residue = df_queue["Residue"].iloc[latest_idx]
current_time = df_queue["Time"].iloc[latest_idx]

# Logic for "Hints" based on residue density
if current_residue > 150:
    status_label = "CRITICAL"
    status_color = "error"
    hint_text = "The park is currently over-saturated. Probable wait time exceeds 40 minutes."
elif current_residue > 70:
    status_label = "BUSY"
    status_color = "warning"
    hint_text = "High volume observed. Large buses (Marcopolo/CNG) are being prioritized for clearing."
else:
    status_label = "MODERATE"
    status_color = "success"
    hint_text = "Standard movement. Queues are being cleared effectively by the current fleet."

st.subheader(f"Status Hint for {current_time}")
st.status(f"Current Condition: **{status_label}** — {hint_text}", state=status_color)

# --- SECTION 2: VOLUME VISUALIZATION ---
st.divider()
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("#### Hourly Queue Trend (Inflow vs. Residue)")
    fig = go.Figure()
    # Inflow Line
    fig.add_trace(go.Scatter(x=df_queue["Time"], y=df_queue["Students_Joining"], 
                             name="Joining Queue", line=dict(color='#1f77b4', width=3)))
    # Residue Bars
    fig.add_trace(go.Bar(x=df_queue["Time"], y=df_queue["Residue"], 
                         name="Residue (Left Behind)", marker_color='#ff7f0e', opacity=0.7))
    
    fig.update_layout(hovermode="x unified", legend=dict(orientation="h", y=1.1),
                      xaxis_title="Time Interval", yaxis_title="Number of Students")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("#### Peak Hour Analytics")
    peak_val = df_queue["Students_Joining"].max()
    peak_time = df_queue.loc[df_queue["Students_Joining"].idxmax(), "Time"]
    
    st.metric("Peak Inflow", f"{peak_val} Students", delta=f"At {peak_time}")
    
    st.write("**Operational Notes:**")
    st.caption("- Peak arrival occurs between 09:45 and 10:15.")
    st.caption("- Marcopolo turnaround time is approximately 18-20 minutes.")
    st.caption("- Tricycle constant flow: ~15 units (4 passengers each) baseline.")

# --- SECTION 3: INTERACTIVE HISTORICAL LOOKUP ---
st.divider()
st.markdown("#### 🔍 Historical Probability Lookup")
st.write("Select a time of day to see the probable condition you will meet at the park.")

selected_time = st.select_slider("Time Window", options=df_queue["Time"].tolist())
search_result = df_queue[df_queue["Time"] == selected_time].iloc[0]

res_val = search_result["Residue"]
if res_val > 100:
    prob_hint = "High likelihood of long queues. Plan for a 30+ minute wait."
else:
    prob_hint = "Likelihood of fast boarding is high."

st.write(f"At **{selected_time}**, the recorded residue was **{res_val} people**. {prob_hint}")

# --- SECTION 4: FLEET MIX ---
with st.expander("View Vehicle Capacity Specifications"):
    st.table(pd.DataFrame(list(vehicle_caps.items()), columns=["Vehicle Type", "Passenger Capacity"]))

# --- FOOTER ---
st.markdown("---")
st.caption("Developed for the 2026 University of Ilorin Transport Research Project | Data Source: Group Observation Logs")
