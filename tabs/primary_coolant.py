# tabs/primary_coolant.py
import streamlit as st

import utils  # Import helpers from utils.py


# --- Specific Helper Function(s) for this Tab ---

def display_pump_status(pump_index):
    """
    Displays status metrics for a single circulation pump,
    using st.status for visual indication.
    """
    st.subheader(f"Circulation Pump {pump_index}")

    # Define the mapping from status code to description and st.status state
    status_map = {
        0: {"desc": "Inactive", "state": "complete"},
        1: {"desc": "Active (No Speed)", "state": "running"},
        2: {"desc": "Active (Speed Reached)", "state": "running"},
        3: {"desc": "Maintenance Required", "state": "error"},
        4: {"desc": "Not Installed", "state": "error"},
        5: {"desc": "Insufficient Energy", "state": "error"}
    }

    # --- Fetch Pump Status Code ---
    status_code_var = f"COOLANT_CORE_CIRCULATION_PUMP_{pump_index}_STATUS"
    status_code_val = utils.fetch_variable_value(status_code_var)

    # Determine status label and state for st.status
    status_label = f"Pump {pump_index}: Unknown"
    status_state = "error"  # Default to error state
    status_description = "Unknown"  # For potential internal use if needed

    if isinstance(status_code_val, (int, float)):
        status_code_int = int(status_code_val)
        if status_code_int in status_map:
            status_info = status_map[status_code_int]
            status_description = status_info["desc"]
            status_state = status_info["state"]
            status_label = f"Pump {pump_index}: {status_description}"
        else:
            status_description = f"Unknown Code ({status_code_int})"
            status_label = f"Pump {pump_index}: {status_description}"
            status_state = "error"
    elif isinstance(status_code_val, str) and "Error:" in status_code_val:
        status_description = "Error Fetching Status"
        status_label = f"Pump {pump_index}: {status_description}"
        status_state = "error"
    else:
        # Handle unexpected non-numeric, non-error values if necessary
        status_description = f"Invalid Status ({status_code_val})"
        status_label = f"Pump {pump_index}: {status_description}"
        status_state = "error"

    # --- Use st.status to display pump details ---
    with st.status(label=status_label, state=status_state, expanded=True):
        # Display other metrics inside the status box using columns
        cols = st.columns(3)
        with cols[0]:
            # Display Dry and Overload Status
            utils.display_metric(f"Dry Status",
                                 f"COOLANT_CORE_CIRCULATION_PUMP_{pump_index}_DRY_STATUS",
                                 help_text="1: Active without fluid, 4: Inactive or OK")
            utils.display_metric(f"Overload",
                                 f"COOLANT_CORE_CIRCULATION_PUMP_{pump_index}_OVERLOAD_STATUS",
                                 help_text="1: Active & Overload, 4: Inactive or OK")
        with cols[1]:
            utils.display_metric(f"Speed (Actual)",
                                 f"COOLANT_CORE_CIRCULATION_PUMP_{pump_index}_SPEED")
        with cols[2]:
            utils.display_metric(f"Speed (Ordered)",
                                 f"COOLANT_CORE_CIRCULATION_PUMP_{pump_index}_ORDERED_SPEED")


def display_overview():
    """Displays the overview metrics for the primary coolant."""
    st.subheader("Coolant Overview")
    with st.container(border=True):
        # Display other metrics in columns first
        cols = st.columns(3)
        with cols[0]:
            # --- Coolant Pressure Gauge ---
            utils.display_gauge(
                title="Coolant Pressure",
                value_var="COOLANT_CORE_PRESSURE",
                range_min_input=0,  # Assuming pressure starts at 0
                range_max_input="COOLANT_CORE_MAX_PRESSURE",  # Use available max pressure variable
                # No specific operative pressure variable for coolant, let gauge use default logic
                unit="bar"  # Assuming bar, adjust if needed
            )
        with cols[1]:
            utils.display_metric("Coolant State Code", "COOLANT_CORE_STATE")
            utils.display_metric("Vessel Temp (°C)", "COOLANT_CORE_VESSEL_TEMPERATURE")
            utils.display_metric("Primary Loop Level", "COOLANT_CORE_PRIMARY_LOOP_LEVEL")
        with cols[2]:
            utils.display_metric("Quantity in Vessel", "COOLANT_CORE_QUANTITY_IN_VESSEL")
            utils.display_metric("Flow Speed (Actual)", "COOLANT_CORE_FLOW_SPEED")
            st.caption(f"Ordered: {utils.fetch_variable_value('COOLANT_CORE_FLOW_ORDERED_SPEED')}")


# --- Main Display Function for the Tab ---

def display_tab():
    """Displays the content for the Primary Coolant tab (Overview then Pumps)."""
    st.header("Primary Coolant Circuit")

    # --- Display Overview Section ---
    display_overview()

    st.divider()  # Add a divider between overview and pumps

    # --- Display details for ALL pumps (2, 1, 0) ---
    st.subheader("Circulation Pump Status")  # Updated subheader

    # Loop from 2 down to 0
    for i in range(2, -1, -1):
        display_pump_status(i)  # Now uses st.status
        # No divider needed between pumps as st.status provides separation
