# main.py
import datetime

import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from streamlit_option_menu import option_menu

# Import configuration and utility functions
import config
import utils
# Import tab display functions
from tabs import overview, core_status, primary_coolant, power_gen, health, raw_data

# --- Initialize Session State ---
# Initialize History DataFrames
if 'core_temp_history' not in st.session_state:
    st.session_state.core_temp_history = pd.DataFrame(columns=['Timestamp', 'Core Temp (°C)'])
if 'total_kw_history' not in st.session_state:
    st.session_state.total_kw_history = pd.DataFrame(columns=['Timestamp', 'Total Output (kW)'])
# Initialize Previous Values for Delta Calculations (add others as needed)
if 'previous_total_kw' not in st.session_state:
    st.session_state.previous_total_kw = None  # Initialize as None

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

# --- Data Update Logic for History & Calculations ---
current_time = datetime.datetime.now()

# Calculate Total Power
total_kw = 0.0
active_generators = 0
for i in range(3):
    kw_value = utils.fetch_variable_value(f"GENERATOR_{i}_KW")
    if isinstance(kw_value, float):
        breaker_val = utils.fetch_variable_value(f"GENERATOR_{i}_BREAKER")
        if isinstance(breaker_val, bool) and not breaker_val:
            total_kw += kw_value
            if kw_value > 0: active_generators += 1

# --- Calculate Delta for Total KW ---
total_kw_delta = None
previous_total_kw = st.session_state.get('previous_total_kw', None)  # Use .get for safety
if previous_total_kw is not None and isinstance(total_kw, (int, float)):
    raw_delta = total_kw - previous_total_kw
    if raw_delta != 0:
        total_kw_delta = raw_delta  # Store raw delta for st.metric

# Update Session State for next run *after* calculating delta
st.session_state['previous_total_kw'] = total_kw
# --- End Delta Calculation ---

# Update Total KW History
new_kw_data = pd.DataFrame({'Timestamp': [current_time], 'Total Output (kW)': [total_kw]})
st.session_state.total_kw_history = pd.concat([st.session_state.total_kw_history, new_kw_data], ignore_index=True)
if len(st.session_state.total_kw_history) > config.MAX_HISTORY_POINTS:
    st.session_state.total_kw_history = st.session_state.total_kw_history.tail(config.MAX_HISTORY_POINTS)

# Update Core Temp History (will get delta automatically via utils.display_metric if displayed)
current_core_temp = utils.fetch_variable_value("CORE_TEMP")
if isinstance(current_core_temp, (int, float)):
    new_temp_data = pd.DataFrame({'Timestamp': [current_time], 'Core Temp (°C)': [current_core_temp]})
    st.session_state.core_temp_history = pd.concat([st.session_state.core_temp_history, new_temp_data],
                                                   ignore_index=True)
    if len(st.session_state.core_temp_history) > config.MAX_HISTORY_POINTS:
        st.session_state.core_temp_history = st.session_state.core_temp_history.tail(config.MAX_HISTORY_POINTS)


# --- Main Display Area using streamlit-option-menu ---
tab_titles = ["Overview", "Core Status", "Primary Coolant", "Steam & Power Gen", "Plant Health & Resources",
              "Raw Data Viewer"]
tab_icons = ['house', 'activity', 'droplet-half', 'lightning-charge', 'heart-pulse', 'list-task']

selected_tab_title = option_menu(
    menu_title=None, options=tab_titles, icons=tab_icons, menu_icon="cast",
    default_index=0, orientation="horizontal",
    styles={  # Styles remain the same...
        "container": {"padding": "5px 0px", "background-color": "transparent", "border-bottom": "1px solid #CCCCCC",
                      "margin-bottom": "15px"},
        "icon": {"color": "#55596A", "font-size": "18px"},
        "nav-link": {"font-size": "16px", "font-weight": "normal", "text-align": "center", "margin": "0px 5px",
                     "padding": "8px 12px", "--hover-color": "#eee", "border-radius": "0px", "border": "none",
                     "background-color": "transparent", "color": "#55596A", "border-bottom": "2px solid transparent"},
        "nav-link-selected": {"background-color": "transparent", "font-weight": "bold", "color": "#007BFF",
                              "border-bottom": "2px solid #007BFF"},
    }
)

# Conditionally display content based on the selected option_menu item
if selected_tab_title == "Overview":
    # Pass total_kw AND its calculated delta to the overview tab
    overview.display_tab(total_kw=total_kw, total_kw_delta=total_kw_delta)
elif selected_tab_title == "Core Status":
    core_status.display_tab()
elif selected_tab_title == "Primary Coolant":
    primary_coolant.display_tab()
elif selected_tab_title == "Steam & Power Gen":
    # The total KW metric in power_gen tab also needs the delta
    # For simplicity, we can recalculate it there or pass it (passing is cleaner)
    # Let's assume power_gen calculates its own display if needed or uses utils.display_metric
    power_gen.display_tab()  # Modify power_gen.display_tab if it shows total KW metric directly
elif selected_tab_title == "Plant Health & Resources":
    health.display_tab()
elif selected_tab_title == "Raw Data Viewer":
    raw_data.display_tab()

