# main.py
import datetime

import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# Import configuration and utility functions
import config
import utils  # Although fetch might be called implicitly via helpers
# Import tab display functions
from tabs import core_status, primary_coolant, power_gen, health, raw_data

# --- Initialize Session State ---
if 'core_temp_history' not in st.session_state:
    st.session_state.core_temp_history = pd.DataFrame(columns=['Timestamp', 'Core Temp (°C)'])
# Add other history initializations here if needed

# --- Streamlit App Layout ---
st.set_page_config(layout="wide")
st.title("Reactor Simulation Dashboard")

# --- Sidebar ---
st.sidebar.header("Settings")
auto_refresh_on = st.sidebar.checkbox("Enable Auto-Refresh", value=True)
refresh_interval = st.sidebar.slider(
    "Refresh Rate (seconds)", 1, 10, config.DEFAULT_REFRESH_RATE_SECONDS,
    disabled=not auto_refresh_on
)
st.sidebar.markdown("---")
st.sidebar.caption("Ensure the simulation's webserver is active.")

# --- Autorefresh Control ---
if auto_refresh_on:
    st_autorefresh(interval=refresh_interval * 1000, key="data_refresher")

# --- Data Update Logic for History ---
# (Keep this logic in main.py as it updates session_state)
current_core_temp = utils.fetch_variable_value("CORE_TEMP")  # Use utils function
current_time = datetime.datetime.now()
if isinstance(current_core_temp, (int, float)):
    new_data = pd.DataFrame({'Timestamp': [current_time], 'Core Temp (°C)': [current_core_temp]})
    st.session_state.core_temp_history = pd.concat([st.session_state.core_temp_history, new_data], ignore_index=True)
    if len(st.session_state.core_temp_history) > config.MAX_HISTORY_POINTS:
        st.session_state.core_temp_history = st.session_state.core_temp_history.tail(config.MAX_HISTORY_POINTS)
# Add update logic for other history data here

# --- Main Display Area using Tabs ---
tab_titles = [
    "Core Status",
    "Primary Coolant",
    "Steam & Power Gen",
    "Plant Health & Resources",
    "Raw Data Viewer"
]
tabs = st.tabs(tab_titles)

with tabs[0]:
    core_status.display_tab()  # Call function from imported module

with tabs[1]:
    primary_coolant.display_tab()  # Call function from imported module

with tabs[2]:
    power_gen.display_tab()  # Call function from imported module

with tabs[3]:
    health.display_tab()  # Call function from imported module

with tabs[4]:
    raw_data.display_tab()  # Call function from imported module

# --- Footer ---
# st.markdown("---")
# st.caption("Dashboard for Nuclear Reactor Simulator")