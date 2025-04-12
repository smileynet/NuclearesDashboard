# ```python
import datetime  # Import datetime for timestamps

import pandas as pd  # Import pandas
import plotly.graph_objects as go  # Import Plotly GO
import requests
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# --- Configuration ---
WEBSERVER_URL = "http://localhost:8785/"
# VARIABLES list remains the same...
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
DEFAULT_REFRESH_RATE_SECONDS = 2
MAX_HISTORY_POINTS = 30  # Keep last 30 data points for charts

# --- Initialize Session State for History ---
if 'core_temp_history' not in st.session_state:
    st.session_state.core_temp_history = pd.DataFrame(columns=['Timestamp', 'Core Temp (°C)'])

# --- Helper Function ---
@st.cache_data(ttl=DEFAULT_REFRESH_RATE_SECONDS * 0.9)  # Cache data slightly less than refresh rate
def fetch_variable_value(variable_name):
    """Fetches a single variable's value from the webserver."""
    # Ensure variable_name is a string before making the request
    if not isinstance(variable_name, str):
        return f"Error: Invalid variable name type ({type(variable_name)})"

    params = {"Variable": variable_name}
    value = f"Error: Var '{variable_name}' not found"  # Default if not fetched
    try:
        response = requests.get(WEBSERVER_URL, params=params, timeout=1)
        response.raise_for_status()
        value = response.text.strip()
        try:
            value = float(value)
        except ValueError:
            if value.upper() == 'TRUE':
                value = True
            elif value.upper() == 'FALSE':
                value = False
    except requests.exceptions.ConnectionError:
        value = "Error: Connection refused."
    except requests.exceptions.Timeout:
        value = "Error: Timeout."
    except requests.exceptions.RequestException as e:
        value = f"Error: {e}"  # Catch other potential request errors
    return value

# --- Helper Display Functions ---
def display_metric(label, variable_name, help_text=None):
    """Fetches and displays a single metric."""
    value = fetch_variable_value(variable_name)
    if isinstance(value, str) and "Error:" in value:
        st.metric(label=label, value="N/A", delta=value, delta_color="off", help=help_text)
    else:
        if isinstance(value, float):
            st.metric(label=label, value=f"{value:.2f}", help=help_text)
        elif isinstance(value, bool):
            st.metric(label=label, value="TRUE" if value else "FALSE", help=help_text)
        else:
            st.metric(label=label, value=value, help=help_text)


# --- UPDATED GAUGE HELPER FUNCTION ---
def display_gauge(title, value_var, range_min_input, range_max_input, op_min_input=None, op_max_input=None, unit=""):
    """
    Fetches data and displays a Plotly gauge chart.
    Range inputs can be variable names (str) or direct numerical values.
    """
    # Fetch the main value
    value = fetch_variable_value(value_var)

    # Determine range_min: Fetch if string, use directly if number
    if isinstance(range_min_input, str):
        range_min = fetch_variable_value(range_min_input)
    elif isinstance(range_min_input, (int, float)):
        range_min = range_min_input
    else:
        range_min = f"Error: Invalid type for range_min ({type(range_min_input)})"

    # Determine range_max: Fetch if string, use directly if number
    if isinstance(range_max_input, str):
        range_max = fetch_variable_value(range_max_input)
    elif isinstance(range_max_input, (int, float)):
        range_max = range_max_input
    else:
        range_max = f"Error: Invalid type for range_max ({type(range_max_input)})"

    # Determine op_min: Fetch if string, use directly if number, else None
    if isinstance(op_min_input, str):
        op_min = fetch_variable_value(op_min_input)
    elif isinstance(op_min_input, (int, float)):
        op_min = op_min_input
    else:
        op_min = None  # Handles None input or invalid types

    # Determine op_max: Fetch if string, use directly if number, else None
    if isinstance(op_max_input, str):
        op_max = fetch_variable_value(op_max_input)
    elif isinstance(op_max_input, (int, float)):
        op_max = op_max_input
    else:
        op_max = None  # Handles None input or invalid types

    # Check if all essential values are valid numbers AFTER determining them
    essential_values = [value, range_min, range_max]
    if not all(isinstance(v, (int, float)) for v in essential_values):
        st.warning(f"Cannot display gauge for '{title}': Invalid data received.")
        # Show the potentially problematic values
        st.caption(f"Value: {value}, Min: {range_min}, Max: {range_max}, OpMin: {op_min}, OpMax: {op_max}")
        return

    # Ensure min < max AFTER confirming they are numbers
    if range_min >= range_max:
        st.warning(f"Cannot display gauge for '{title}': Min range ({range_min}) >= Max range ({range_max}).")
        return

    # Determine steps and colors based on operative range availability
    steps = []
    # Check op_min and op_max are valid numbers before using them
    op_min_valid = isinstance(op_min, (int, float))
    op_max_valid = isinstance(op_max, (int, float))

    if op_min_valid and op_max_valid:
        # Three zones: Below Op, Operative, Above Op
        steps = [
            {'range': [range_min, op_min], 'color': "lightblue"},
            {'range': [op_min, op_max], 'color': "lightgreen"},
            {'range': [op_max, range_max], 'color': "lightcoral"}
        ]
        threshold_value = op_max  # Use operative max as a visual threshold line
    elif op_max_valid:
        # Two zones: Below Op Max, Above Op Max (e.g., Pressure)
        steps = [
            {'range': [range_min, op_max], 'color': "lightgreen"},
            {'range': [op_max, range_max], 'color': "lightcoral"}
        ]
        threshold_value = op_max
    else:
        # Default single color if no operative range
        steps = [{'range': [range_min, range_max], 'color': "lightgray"}]
        threshold_value = range_max  # Use max range as threshold

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"{title} ({unit})" if unit else title, 'font': {'size': 18}},  # Smaller font size
        gauge={
            'axis': {'range': [range_min, range_max], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': steps,
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': threshold_value
            }
        }
    ))
    # Adjust layout for smaller size
    fig.update_layout(
        height=200,  # Reduced height
        margin=dict(l=20, r=20, t=40, b=20),  # Adjusted margins
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
        font={'color': "gray", 'family': "Arial"}  # Match theme potentially
    )
    st.plotly_chart(fig, use_container_width=True)  # Use container width


# --- Other Helper Display Functions ---
# (display_progress, display_pump_status, etc. remain the same)
def display_progress(label, variable_name, max_value=100, help_text=None):
    """Fetches and displays a progress bar."""
    value = fetch_variable_value(variable_name)
    if isinstance(value, (int, float)):
        progress_value = max(0.0, min(float(value), float(max_value))) / float(max_value)
        st.text(label)
        st.progress(progress_value, text=f"{value:.1f}%" if max_value == 100 else f"{value:.1f}")
    else:
        st.text(f"{label}: N/A ({value})")

def display_pump_status(pump_index):
    """Displays status metrics for a single circulation pump."""
    st.subheader(f"Circulation Pump {pump_index}")
    cols = st.columns(3)
    with cols[0]:
        display_metric(f"Pump {pump_index} Status Code", f"COOLANT_CORE_CIRCULATION_PUMP_{pump_index}_STATUS")
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
    with cols[0]: display_metric(f"Turbine {turbine_index} RPM", f"STEAM_TURBINE_{turbine_index}_RPM")
    with cols[1]: display_metric(f"Turbine {turbine_index} Temp (°C)", f"STEAM_TURBINE_{turbine_index}_TEMPERATURE")
    with cols[2]: display_metric(f"Turbine {turbine_index} Pressure", f"STEAM_TURBINE_{turbine_index}_PRESSURE")

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
        display_metric(f"Gen {gen_index} Breaker", f"GENERATOR_{gen_index}_BREAKER",
                       help_text="TRUE: Open, FALSE: Close")


# --- Streamlit App Layout ---
st.set_page_config(layout="wide")
st.title("Reactor Simulation Dashboard")

# --- Sidebar ---
st.sidebar.header("Settings")
auto_refresh_on = st.sidebar.checkbox("Enable Auto-Refresh", value=True)
refresh_interval = st.sidebar.slider(
    "Refresh Rate (seconds)", 1, 10, DEFAULT_REFRESH_RATE_SECONDS,
    disabled=not auto_refresh_on
)
st.sidebar.markdown("---")
st.sidebar.caption("Ensure the simulation's webserver is active.")

# --- Autorefresh Control ---
if auto_refresh_on:
    st_autorefresh(interval=refresh_interval * 1000, key="data_refresher")

# --- Data Update Logic for History ---
current_core_temp = fetch_variable_value("CORE_TEMP")
current_time = datetime.datetime.now()
if isinstance(current_core_temp, (int, float)):
    new_data = pd.DataFrame({'Timestamp': [current_time], 'Core Temp (°C)': [current_core_temp]})
    st.session_state.core_temp_history = pd.concat([st.session_state.core_temp_history, new_data], ignore_index=True)
    if len(st.session_state.core_temp_history) > MAX_HISTORY_POINTS:
        st.session_state.core_temp_history = st.session_state.core_temp_history.tail(MAX_HISTORY_POINTS)

# --- Main Display Area using Tabs ---
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
    # Use columns for Temp and Pressure gauges side-by-side
    gauge_cols = st.columns(2)
    with gauge_cols[0]:
        # --- Core Temp Gauge ---
        # Call arguments are now variable names (strings)
        display_gauge(
            title="Core Temperature",
            value_var="CORE_TEMP",
            range_min_input="CORE_TEMP_MIN",  # Pass var name
            range_max_input="CORE_TEMP_MAX",  # Pass var name
            op_min_input="CORE_TEMP_OPERATIVE",  # Pass var name
            op_max_input="CORE_TEMP_MAX",  # Using CORE_TEMP_MAX as end of operative for gauge coloring
            unit="°C"
        )
    with gauge_cols[1]:
        # --- Core Pressure Gauge ---
        # Call arguments use 0 directly for min, var names for others
        display_gauge(
            title="Core Pressure",
            value_var="CORE_PRESSURE",
            range_min_input=0,  # Pass number 0 directly
            range_max_input="CORE_PRESSURE_MAX",  # Pass var name
            op_max_input="CORE_PRESSURE_OPERATIVE",  # Pass var name
            unit="bar"  # Assuming bar, adjust if needed
        )

    st.divider()
    # --- Other Core Metrics ---
    other_core_cols = st.columns(3)
    with other_core_cols[0]:
        display_metric("Core State Code", "CORE_STATE")
        display_metric("Core State Criticality", "CORE_STATE_CRITICALITY")
    with other_core_cols[1]:
        # Keep criticality statuses
        display_metric("Critical Mass Reached?", "CORE_CRITICAL_MASS_REACHED")
    with other_core_cols[2]:
        display_metric("Imminent Fusion?", "CORE_IMMINENT_FUSION")
        display_metric("Ready for Start?", "CORE_READY_FOR_START")

    st.divider()
    # --- Core Temp History Chart ---
    st.subheader("Core Temperature History")
    if not st.session_state.core_temp_history.empty:
        chart_df = st.session_state.core_temp_history.set_index('Timestamp')
        st.line_chart(chart_df)
    else:
        st.caption("Collecting temperature data for chart...")
    st.divider()

    # --- Control Rods Section ---
    st.subheader("Control Rods")
    cols_rods = st.columns(4)
    with cols_rods[0]:
        display_metric("Rods Status Code", "RODS_STATUS")
        display_metric("Rods Quantity", "RODS_QUANTITY")
    with cols_rods[1]:
        display_metric("Rods Pos (Actual)", "RODS_POS_ACTUAL")
        display_metric("Rods Pos (Ordered)", "RODS_POS_ORDERED")
    with cols_rods[2]:
        display_metric("Rods Movement Speed", "RODS_MOVEMENT_SPEED")
        display_metric("Rods Temp (°C)", "RODS_TEMPERATURE")
        st.caption(f"Max Temp: {fetch_variable_value('RODS_MAX_TEMPERATURE')}")
    with cols_rods[3]:
        display_metric("Rods Aligned?", "RODS_ALIGNED")
        display_metric("Rods Deformed?", "RODS_DEFORMED")

with tabs[1]:  # Primary Coolant Tab
    # ... (Primary Coolant content remains the same) ...
    st.header("Primary Coolant Circuit")
    cols = st.columns(3)
    with cols[0]:
        display_metric("Coolant State Code", "COOLANT_CORE_STATE")
        display_metric("Coolant Pressure", "COOLANT_CORE_PRESSURE")
        st.caption(f"Max: {fetch_variable_value('COOLANT_CORE_MAX_PRESSURE')}")
    with cols[1]:
        display_metric("Vessel Temp (°C)", "COOLANT_CORE_VESSEL_TEMPERATURE")
        display_metric("Primary Loop Level", "COOLANT_CORE_PRIMARY_LOOP_LEVEL")
    with cols[2]:
        display_metric("Quantity in Vessel", "COOLANT_CORE_QUANTITY_IN_VESSEL")
        display_metric("Flow Speed (Actual)", "COOLANT_CORE_FLOW_SPEED")
        st.caption(f"Ordered: {fetch_variable_value('COOLANT_CORE_FLOW_ORDERED_SPEED')}")
    st.divider()

    num_pumps = fetch_variable_value("COOLANT_CORE_QUANTITY_CIRCULATION_PUMPS_PRESENT")
    if isinstance(num_pumps, (int, float)) and num_pumps >= 0:
        for i in range(int(num_pumps)):
            display_pump_status(i)
            st.divider()
    else:
        st.warning(f"Could not determine number of pumps or invalid value: {num_pumps}")

with tabs[2]:  # Steam & Power Gen Tab
    # ... (Steam & Power Gen content remains the same) ...
    st.header("Steam & Power Generation")
    cols_steam = st.columns(2)
    with cols_steam[0]:
        display_metric("Steam Present?", "CORE_STEAM_PRESENT")
    with cols_steam[1]:
        display_metric("High Steam Present?", "CORE_HIGH_STEAM_PRESENT")
    st.divider()

    for i in range(3):
        rpm_value = fetch_variable_value(f"STEAM_TURBINE_{i}_RPM")
        if not (isinstance(rpm_value, str) and "Error:" in rpm_value):
            display_turbine_status(i)
            st.divider()

    total_kw = 0.0
    for i in range(3):
        kw_value = fetch_variable_value(f"GENERATOR_{i}_KW")
        if not (isinstance(kw_value, str) and "Error:" in kw_value):
            display_generator_status(i)
            st.divider()
            if isinstance(kw_value, float): total_kw += kw_value
    st.header(f"Total Generator Output: {total_kw:.2f} kW")

with tabs[3]:  # Plant Health & Resources Tab
    st.header("Plant Health & Resources")
    # Replace progress bars with gauges
    health_cols = st.columns(3)
    with health_cols[0]:
        st.subheader("Core Health")
        # --- Core Integrity Gauge ---
        # Pass direct numbers for min/max range
        display_gauge(
            title="Core Integrity",
            value_var="CORE_INTEGRITY",
            range_min_input=0, range_max_input=100,
            unit="%"
        )
        # --- Core Wear Gauge ---
        display_gauge(
            title="Core Wear",
            value_var="CORE_WEAR",
            range_min_input=0, range_max_input=100,
            unit="%"
        )
    with health_cols[1]:
        st.subheader("Rod Health")
        display_metric("Rods Temp (°C)", "RODS_TEMPERATURE")
        st.caption(f"Max Temp: {fetch_variable_value('RODS_MAX_TEMPERATURE')}")
        display_metric("Rods Deformed?", "RODS_DEFORMED")
    with health_cols[2]:
        st.subheader("Time")
        display_metric("Sim Time", "TIME")
        display_metric("Timestamp", "TIME_STAMP")
    st.divider()

    st.subheader("Future / Other")
    st.markdown("""
        * **Fuel Level:** (Variable Needed - *Good candidate for Gauge*)
        * **Component Wear (Pumps, Turbines):** (Variables Needed - *Gauges?*)
        * **Prestige/XP:** (Variables Needed - *Metrics*)
        * **Energy Demand:** (Variable Needed - *Metric/Chart*)
        * **Chemical Status (Boron, pH, Xenon):** (Variables Needed - *Metrics/Charts*)
        * **AO Status:** (Variables Needed - *Text/Indicators*)
    """)

with tabs[4]:  # Raw Data Viewer
    # ... (Raw Data Viewer content remains the same) ...
    st.header("Raw Variable Viewer")
    st.info("Select variables below to view their current raw values.")
    selected_variables_raw = st.multiselect(
        "Select variables to view:", options=VARIABLES,
        default=["CORE_TEMP", "CORE_PRESSURE", "TIME_STAMP"],
        key="raw_data_multiselect"
    )
    if not selected_variables_raw:
        st.warning("Select variables above to view their raw values.")
    else:
        num_columns_raw = 3
        cols_raw = st.columns(num_columns_raw)
        for i, variable in enumerate(selected_variables_raw):
            col_index = i % num_columns_raw
            with cols_raw[col_index]: display_metric(variable, variable)

# --- Footer ---
# st.markdown("---")
# st.caption("Dashboard for Nuclear Reactor Simulator")

# ```
#
