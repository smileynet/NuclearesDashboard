import time

import requests
import streamlit as st

# --- Configuration ---
WEBSERVER_URL = "http://localhost:8080/"
VARIABLES = [
    # Core
    "CORE_TEMP", "CORE_TEMP_OPERATIVE", "CORE_TEMP_MAX", "CORE_TEMP_MIN", "CORE_TEMP_RESIDUAL",
    "CORE_PRESSURE", "CORE_PRESSURE_MAX", "CORE_PRESSURE_OPERATIVE", "CORE_INTEGRITY", "CORE_WEAR",
    "CORE_STATE", "CORE_STATE_CRITICALITY", "CORE_CRITICAL_MASS_REACHED", "CORE_CRITICAL_MASS_REACHED_COUNTER",
    "CORE_IMMINENT_FUSION", "CORE_READY_FOR_START", "CORE_STEAM_PRESENT", "CORE_HIGH_STEAM_PRESENT",
    # Time
    "TIME", "TIME_STAMP",
    # Coolant Core
    "COOLANT_CORE_STATE", "COOLANT_CORE_PRESSURE", "COOLANT_CORE_MAX_PRESSURE", "COOLANT_CORE_VESSEL_TEMPERATURE",
    "COOLANT_CORE_QUANTITY_IN_VESSEL", "COOLANT_CORE_PRIMARY_LOOP_LEVEL", "COOLANT_CORE_FLOW_SPEED",
    "COOLANT_CORE_FLOW_ORDERED_SPEED", "COOLANT_CORE_FLOW_REACHED_SPEED",
    "COOLANT_CORE_QUANTITY_CIRCULATION_PUMPS_PRESENT", "COOLANT_CORE_QUANTITY_FREIGHT_PUMPS_PRESENT",
    # Coolant Core Pumps (0-2)
    "COOLANT_CORE_CIRCULATION_PUMP_0_STATUS", "COOLANT_CORE_CIRCULATION_PUMP_1_STATUS",
    "COOLANT_CORE_CIRCULATION_PUMP_2_STATUS",
    "COOLANT_CORE_CIRCULATION_PUMP_0_DRY_STATUS", "COOLANT_CORE_CIRCULATION_PUMP_1_DRY_STATUS",
    "COOLANT_CORE_CIRCULATION_PUMP_2_DRY_STATUS",
    "COOLANT_CORE_CIRCULATION_PUMP_0_OVERLOAD_STATUS", "COOLANT_CORE_CIRCULATION_PUMP_1_OVERLOAD_STATUS",
    "COOLANT_CORE_CIRCULATION_PUMP_2_OVERLOAD_STATUS",
    "COOLANT_CORE_CIRCULATION_PUMP_0_ORDERED_SPEED", "COOLANT_CORE_CIRCULATION_PUMP_1_ORDERED_SPEED",
    "COOLANT_CORE_CIRCULATION_PUMP_2_ORDERED_SPEED",
    "COOLANT_CORE_CIRCULATION_PUMP_0_SPEED", "COOLANT_CORE_CIRCULATION_PUMP_1_SPEED",
    "COOLANT_CORE_CIRCULATION_PUMP_2_SPEED",
    # Rods
    "RODS_STATUS", "RODS_MOVEMENT_SPEED", "RODS_MOVEMENT_SPEED_DECREASED_HIGH_TEMPERATURE", "RODS_DEFORMED",
    "RODS_TEMPERATURE", "RODS_MAX_TEMPERATURE", "RODS_POS_ORDERED", "RODS_POS_ACTUAL", "RODS_POS_REACHED",
    "RODS_QUANTITY", "RODS_ALIGNED",
    # Generator (0-2) - Patch V 1.2.19.159
    "GENERATOR_0_KW", "GENERATOR_1_KW", "GENERATOR_2_KW",
    "GENERATOR_0_V", "GENERATOR_1_V", "GENERATOR_2_V",
    "GENERATOR_0_A", "GENERATOR_1_A", "GENERATOR_2_A",
    "GENERATOR_0_HERTZ", "GENERATOR_1_HERTZ", "GENERATOR_2_HERTZ",
    "GENERATOR_0_BREAKER", "GENERATOR_1_BREAKER", "GENERATOR_2_BREAKER",
    # Steam Turbine (0-2) - Patch V 1.2.19.159
    "STEAM_TURBINE_0_RPM", "STEAM_TURBINE_1_RPM", "STEAM_TURBINE_2_RPM",
    "STEAM_TURBINE_0_TEMPERATURE", "STEAM_TURBINE_1_TEMPERATURE", "STEAM_TURBINE_2_TEMPERATURE",
    "STEAM_TURBINE_0_PRESSURE", "STEAM_TURBINE_1_PRESSURE", "STEAM_TURBINE_2_PRESSURE",
]
REFRESH_RATE_SECONDS = 2  # How often to refresh the data (in seconds)


# --- Helper Function ---
def fetch_variable_value(variable_name):
    """Fetches a single variable's value from the webserver."""
    params = {"Variable": variable_name}
    try:
        response = requests.get(WEBSERVER_URL, params=params, timeout=1)  # Added timeout
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        return response.text.strip()
    except requests.exceptions.ConnectionError:
        return "Error: Connection refused. Is the webserver running?"
    except requests.exceptions.Timeout:
        return "Error: Request timed out."
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"


# --- Streamlit App Layout ---
st.set_page_config(layout="wide")
st.title("Simulation Webserver Dashboard")

st.sidebar.header("Settings")

# Variable Selection
selected_variables = st.sidebar.multiselect(
    "Select variables to display:",
    options=VARIABLES,
    default=["CORE_TEMP", "CORE_PRESSURE", "TIME_STAMP"]  # Sensible defaults
)

# Auto-refresh control
auto_refresh = st.sidebar.checkbox("Enable Auto-Refresh", value=True)
refresh_rate = st.sidebar.slider("Refresh Rate (seconds)", 1, 10, REFRESH_RATE_SECONDS, disabled=not auto_refresh)

st.sidebar.markdown("---")
st.sidebar.caption("Ensure the simulation's webserver is active.")

# --- Data Display Area ---
if not selected_variables:
    st.warning("Please select at least one variable from the sidebar.")
else:
    st.header("Live Data")
    # Create columns for better layout (adjust number as needed)
    num_columns = 3
    cols = st.columns(num_columns)

    # Placeholder for dynamic content
    placeholder = st.empty()

    # --- Main Loop for Displaying Data ---
    while True:
        data_to_display = {}
        with placeholder.container():
            # Fetch data for selected variables
            for i, variable in enumerate(selected_variables):
                value = fetch_variable_value(variable)
                col_index = i % num_columns
                with cols[col_index]:
                    # Display metric with handling for potential errors
                    if "Error:" in str(value):
                        st.metric(label=variable, value="N/A", delta=value, delta_color="off")
                    else:
                        st.metric(label=variable, value=value)

        if not auto_refresh:
            st.sidebar.button("Refresh Manually")  # Button press will trigger rerun
            break  # Exit the loop if auto-refresh is off

        time.sleep(refresh_rate)
        # No explicit rerun needed for auto-refresh, Streamlit handles the loop.
        # However, if using st.experimental_rerun or similar state management later,
        # you might need manual rerun triggers. For this simple case, time.sleep works.

# --- Footer ---
st.markdown("---")
st.caption("App to visualize simulation data from the webserver.")
