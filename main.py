# main.py
import datetime

import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from streamlit_option_menu import option_menu  # Import option_menu

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

# --- Main Display Area using streamlit-option-menu ---
tab_titles = [
    "Core Status",
    "Primary Coolant",
    "Steam & Power Gen",
    "Plant Health & Resources",
    "Raw Data Viewer"
]
# Icons from: https://icons.getbootstrap.com/
tab_icons = ['activity', 'droplet-half', 'lightning-charge', 'heart-pulse', 'list-task']

# Use option_menu for navigation, it persists state automatically
selected_tab_title = option_menu(
    menu_title=None,  # Required, but can be None for no title
    options=tab_titles,  # Required
    icons=tab_icons,  # Optional
    menu_icon="cast",  # Optional
    default_index=0,  # Optional
    orientation="horizontal",
    styles={  # UPDATED STYLES for a flatter, underlined look
        "container": {
            "padding": "5px 0px",  # Add some vertical padding
            "background-color": "transparent",  # Keep transparent background
            "border-bottom": "1px solid #CCCCCC",  # Underline the whole container
            "margin-bottom": "15px",  # Add space below the menu
        },
        "icon": {
            "color": "#55596A",  # Default icon color (medium grey)
            "font-size": "18px"
        },
        "nav-link": {
            "font-size": "16px",
            "font-weight": "normal",  # Normal weight for unselected
            "text-align": "center",
            "margin": "0px 5px",  # Add slight horizontal margin
            "padding": "8px 12px",  # Padding within the link
            "--hover-color": "#eee",  # Hover background color
            "border-radius": "0px",  # No rounded corners
            "border": "none",  # No border
            "background-color": "transparent",  # No background
            "color": "#55596A",  # Text color for unselected (medium grey)
            "border-bottom": "2px solid transparent",  # Placeholder for selected underline
        },
        "nav-link-selected": {
            "background-color": "transparent",  # No background for selected
            "font-weight": "bold",  # Make selected bold
            "color": "#007BFF",  # Primary color for selected text (adjust as needed)
            "border-bottom": "2px solid #007BFF",  # Underline for selected
            # Icon color might inherit the text color here, if not, specific CSS injection needed
        },
    }
)

# Conditionally display content based on the selected option_menu item
if selected_tab_title == tab_titles[0]:
    core_status.display_tab()  # Call function from imported module

elif selected_tab_title == tab_titles[1]:
    primary_coolant.display_tab()  # Call function from imported module

elif selected_tab_title == tab_titles[2]:
    power_gen.display_tab()  # Call function from imported module

elif selected_tab_title == tab_titles[3]:
    health.display_tab()  # Call function from imported module

elif selected_tab_title == tab_titles[4]:
    raw_data.display_tab()  # Call function from imported module

# --- Footer ---
# st.markdown("---")
# st.caption("Dashboard for Nuclear Reactor Simulator")
