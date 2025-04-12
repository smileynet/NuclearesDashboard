import requests
import streamlit as st
# Import the autorefresh component
from streamlit_autorefresh import st_autorefresh

# --- Configuration ---
WEBSERVER_URL = "http://localhost:8785/"
# Using the full list provided in the original file
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
DEFAULT_REFRESH_RATE_SECONDS = 2  # How often to refresh the data (in seconds)

# --- Helper Function ---
# Use Streamlit's cache for data fetching to avoid redundant calls within a single run
@st.cache_data(ttl=DEFAULT_REFRESH_RATE_SECONDS * 0.9)  # Cache data slightly less than refresh rate
def fetch_variable_value(variable_name):
    """Fetches a single variable's value from the webserver."""
    params = {"Variable": variable_name}
    value = f"Error: Var '{variable_name}' not found"  # Default if not fetched
    try:
        response = requests.get(WEBSERVER_URL, params=params, timeout=1)  # Added timeout
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        value = response.text.strip()
        # Attempt to convert to float if possible for potential numeric operations
        try:
            value = float(value)
        except ValueError:
            # Handle specific string bools
            if value.upper() == 'TRUE':
                value = True
            elif value.upper() == 'FALSE':
                value = False
            # Keep other strings as is
    except requests.exceptions.ConnectionError:
        value = "Error: Connection refused."
    except requests.exceptions.Timeout:
        value = "Error: Timeout."
    except requests.exceptions.RequestException as e:
        value = f"Error: {e}"  # More specific error
    return value


# --- Helper Display Functions ---
# (These functions now directly call the cached fetch_variable_value)
def display_metric(label, variable_name, help_text=None):
    """Fetches and displays a single metric."""
    value = fetch_variable_value(variable_name)
    if isinstance(value, str) and "Error:" in value:
        st.metric(label=label, value="N/A", delta=value, delta_color="off", help=help_text)
    else:
        # Format floats nicely
        if isinstance(value, float):
            st.metric(label=label, value=f"{value:.2f}", help=help_text)
        elif isinstance(value, bool):
            st.metric(label=label, value="TRUE" if value else "FALSE", help=help_text)
        else:
            st.metric(label=label, value=value, help=help_text)  # Display strings/ints directly


def display_progress(label, variable_name, max_value=100, help_text=None):
    """Fetches and displays a progress bar."""
    value = fetch_variable_value(variable_name)
    if isinstance(value, (int, float)):
        # Ensure value is within 0-max_value range for progress bar
        progress_value = max(0.0, min(float(value), float(max_value))) / float(max_value)
        st.text(label)  # Use st.text for label above progress bar
        st.progress(progress_value,
                    text=f"{value:.1f}%" if max_value == 100 else f"{value:.1f}")  # Show percentage if max is 100
    else:
        st.text(f"{label}: N/A ({value})")  # Show error if value is not numeric


def display_pump_status(pump_index):
    """Displays status metrics for a single circulation pump."""
    st.subheader(f"Circulation Pump {pump_index}")
    cols = st.columns(3)
    with cols[0]:
        display_metric(f"Pump {pump_index} Status Code", f"COOLANT_CORE_CIRCULATION_PUMP_{pump_index}_STATUS")
        # Add helper text for status codes based on prompt
        st.caption(
            "0: Inactive, 1: Active (No Speed), 2: Active (Speed Reached), 3: Maint. Req., 4: Not Installed, 5: No Energy")
        display_metric(f"Pump {pump_index} Dry Status", f"COOLANT_CORE_CIRCULATION_PUMP_{pump_index}_DRY_STATUS",
                       help_text="1: Active without fluid, 4: Inactive or OK")
        display_metric(f"Pump {pump_index} Overload", f"COOLANT_CORE_CIRCULATION_PUMP_{pump_index}_OVERLOAD_STATUS",
                       help_text="1: Active & Overload, 4: Inactive or OK")
    with cols[1]:
        display_metric(f"Pump {pump_index} Speed (Actual)", f"COOLANT_CORE_CIRCULATION_PUMP_{pump_index}_SPEED")
    with cols[2]:
        display_metric(f"Pump {pump_index} Speed (Ordered)",
                       f"COOLANT_CORE_CIRCULATION_PUMP_{pump_index}_ORDERED_SPEED")


def display_turbine_status(turbine_index):
    """Displays status metrics for a single turbine."""
    st.subheader(f"Steam Turbine {turbine_index}")
    cols = st.columns(3)
    with cols[0]:
        display_metric(f"Turbine {turbine_index} RPM", f"STEAM_TURBINE_{turbine_index}_RPM")
    with cols[1]:
        display_metric(f"Turbine {turbine_index} Temp (°C)", f"STEAM_TURBINE_{turbine_index}_TEMPERATURE")
    with cols[2]:
        display_metric(f"Turbine {turbine_index} Pressure", f"STEAM_TURBINE_{turbine_index}_PRESSURE")


def display_generator_status(gen_index):
    """Displays status metrics for a single generator."""
    st.subheader(f"Generator {gen_index}")
    cols = st.columns(3)
    with cols[0]:
        display_metric(f"Gen {gen_index} Output (kW)", f"GENERATOR_{gen_index}_KW")
        display_metric(f"Gen {gen_index} Voltage (V)", f"GENERATOR_{gen_index}_V")
    with cols[1]:
        display_metric(f"Gen {gen_index} Current (A)", f"GENERATOR_{gen_index}_A")
        display_metric(f"Gen {gen_index} Frequency (Hz)", f"GENERATOR_{gen_index}_HERTZ")
    with cols[2]:
        # Handle boolean explicitly now
        breaker_status = fetch_variable_value(f"GENERATOR_{gen_index}_BREAKER")
        display_metric(f"Gen {gen_index} Breaker", f"GENERATOR_{gen_index}_BREAKER",
                       help_text="TRUE: Open, FALSE: Close")

# --- Streamlit App Layout ---
st.set_page_config(layout="wide")
st.title("Reactor Simulation Dashboard")

# Sidebar for settings
st.sidebar.header("Settings")
auto_refresh_on = st.sidebar.checkbox("Enable Auto-Refresh", value=True)
# Slider only enabled if checkbox is ticked
refresh_interval = st.sidebar.slider(
    "Refresh Rate (seconds)", 1, 10, DEFAULT_REFRESH_RATE_SECONDS,
    disabled=not auto_refresh_on
)
st.sidebar.markdown("---")
st.sidebar.caption("Ensure the simulation's webserver is active.")

# --- Autorefresh Control ---
# Conditionally run autorefresh based on checkbox
if auto_refresh_on:
    st_autorefresh(interval=refresh_interval * 1000, key="data_refresher")  # Interval in milliseconds

# --- Main Display Area using Tabs ---
# (This part of the code now runs on every Streamlit rerun, triggered by autorefresh or manually)
tab_titles = [
    "Core Status",
    "Primary Coolant",
    "Steam & Power Gen",
    "Plant Health & Resources",
    "Raw Data Viewer"
]
tabs = st.tabs(tab_titles)

with tabs[0]:  # Core Status Tab
    st.header("Reactor Core Status")
    cols = st.columns(4)
    with cols[0]:
        display_metric("Core State Code", "CORE_STATE")
        display_metric("Core State Criticality", "CORE_STATE_CRITICALITY")
    with cols[1]:
        display_metric("Core Temp (°C)", "CORE_TEMP")
        st.caption(
            f"Op: {fetch_variable_value('CORE_TEMP_OPERATIVE')}, Min: {fetch_variable_value('CORE_TEMP_MIN')}, Max: {fetch_variable_value('CORE_TEMP_MAX')}")
    with cols[2]:
        display_metric("Core Pressure", "CORE_PRESSURE")
        st.caption(
            f"Op: {fetch_variable_value('CORE_PRESSURE_OPERATIVE')}, Max: {fetch_variable_value('CORE_PRESSURE_MAX')}")
    with cols[3]:
        display_metric("Critical Mass Reached?", "CORE_CRITICAL_MASS_REACHED")
        display_metric("Imminent Fusion?", "CORE_IMMINENT_FUSION")
        display_metric("Ready for Start?", "CORE_READY_FOR_START")

    st.divider()
    st.subheader("Control Rods")
    cols = st.columns(4)
    with cols[0]:
        display_metric("Rods Status Code", "RODS_STATUS")
        display_metric("Rods Quantity", "RODS_QUANTITY")
    with cols[1]:
        display_metric("Rods Pos (Actual)", "RODS_POS_ACTUAL")
        display_metric("Rods Pos (Ordered)", "RODS_POS_ORDERED")
    with cols[2]:
        display_metric("Rods Movement Speed", "RODS_MOVEMENT_SPEED")
        display_metric("Rods Temp (°C)", "RODS_TEMPERATURE")
        st.caption(f"Max Temp: {fetch_variable_value('RODS_MAX_TEMPERATURE')}")
    with cols[3]:
        display_metric("Rods Aligned?", "RODS_ALIGNED")
        display_metric("Rods Deformed?", "RODS_DEFORMED")

with tabs[1]:  # Primary Coolant Tab
    st.header("Primary Coolant Circuit")
    cols = st.columns(3)
    with cols[0]:
        display_metric("Coolant State Code", "COOLANT_CORE_STATE")
        display_metric("Coolant Pressure", "COOLANT_CORE_PRESSURE")
        st.caption(f"Max: {fetch_variable_value('COOLANT_CORE_MAX_PRESSURE')}")
    with cols[1]:
        display_metric("Vessel Temp (°C)", "COOLANT_CORE_VESSEL_TEMPERATURE")
        display_metric("Primary Loop Level", "COOLANT_CORE_PRIMARY_LOOP_LEVEL")  # Assuming %
    with cols[2]:
        display_metric("Quantity in Vessel", "COOLANT_CORE_QUANTITY_IN_VESSEL")  # Units?
        display_metric("Flow Speed (Actual)", "COOLANT_CORE_FLOW_SPEED")
        st.caption(f"Ordered: {fetch_variable_value('COOLANT_CORE_FLOW_ORDERED_SPEED')}")

    st.divider()
    # Circulation Pumps - Display status for pumps present
    num_pumps = fetch_variable_value("COOLANT_CORE_QUANTITY_CIRCULATION_PUMPS_PRESENT")
    if isinstance(num_pumps, (int, float)) and num_pumps >= 0:  # Check if valid number
        for i in range(int(num_pumps)):
            display_pump_status(i)
            st.divider()
    else:
        st.warning(f"Could not determine number of pumps or invalid value: {num_pumps}")

with tabs[2]:  # Steam & Power Gen Tab
    st.header("Steam & Power Generation")
    # Steam Presence
    cols_steam = st.columns(2)
    with cols_steam[0]:
        display_metric("Steam Present?", "CORE_STEAM_PRESENT")
    with cols_steam[1]:
        display_metric("High Steam Present?", "CORE_HIGH_STEAM_PRESENT")

    st.divider()
    # Turbines
    # Assuming max 3 turbines based on variable names
    for i in range(3):
        # Basic check if turbine exists (e.g., if RPM is available and not an error)
        rpm_value = fetch_variable_value(f"STEAM_TURBINE_{i}_RPM")
        # Check if it's not an error string before proceeding
        if not (isinstance(rpm_value, str) and "Error:" in rpm_value):
            display_turbine_status(i)
            st.divider()

    # Generators
    total_kw = 0.0
    for i in range(3):
        # Basic check if generator exists (e.g., if KW is available and not an error)
        kw_value = fetch_variable_value(f"GENERATOR_{i}_KW")
        if not (isinstance(kw_value, str) and "Error:" in kw_value):
            display_generator_status(i)
            st.divider()
            if isinstance(kw_value, float):
                total_kw += kw_value

    # Display Total Power
    st.header(f"Total Generator Output: {total_kw:.2f} kW")

with tabs[3]:  # Plant Health & Resources Tab
    st.header("Plant Health & Resources")
    cols = st.columns(3)
    with cols[0]:
        st.subheader("Core Health")
        display_progress("Core Integrity (%)", "CORE_INTEGRITY")
        display_progress("Core Wear (%)", "CORE_WEAR")
    with cols[1]:
        st.subheader("Rod Health")
        display_metric("Rods Temp (°C)", "RODS_TEMPERATURE")
        st.caption(f"Max Temp: {fetch_variable_value('RODS_MAX_TEMPERATURE')}")
        display_metric("Rods Deformed?", "RODS_DEFORMED")
    with cols[2]:
        st.subheader("Time")
        display_metric("Sim Time", "TIME")
        display_metric("Timestamp", "TIME_STAMP")

    # Add placeholders for future variables like Fuel, Prestige, etc.
    st.divider()
    st.subheader("Future / Other")
    st.markdown("""
        * **Fuel Level:** (Variable Needed)
        * **Component Wear (Pumps, Turbines):** (Variables Needed)
        * **Prestige/XP:** (Variables Needed)
        * **Energy Demand:** (Variable Needed)
        * **Chemical Status (Boron, pH, Xenon):** (Variables Needed)
        * **AO Status:** (Variables Needed)
    """)

with tabs[4]:  # Raw Data Viewer
    st.header("Raw Variable Viewer")
    st.info("Select variables below to view their current raw values.")
    # Variable Selection - Using a unique key
    selected_variables_raw = st.multiselect(
        "Select variables to view:",
        options=VARIABLES,
        default=["CORE_TEMP", "CORE_PRESSURE", "TIME_STAMP"],  # Sensible defaults
        key="raw_data_multiselect"  # Keep the unique key
    )
    if not selected_variables_raw:
        st.warning("Select variables above to view their raw values.")
    else:
        num_columns_raw = 3
        cols_raw = st.columns(num_columns_raw)
        # Display selected raw variables
        for i, variable in enumerate(selected_variables_raw):
            col_index = i % num_columns_raw
            with cols_raw[col_index]:
                display_metric(variable, variable)  # Reuses the display logic

# --- Footer --- (optional)
# st.markdown("---")
# st.caption("Dashboard for Nuclear Reactor Simulator")
