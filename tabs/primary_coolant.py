# tabs/primary_coolant.py
import streamlit as st

# Removed: from streamlit_option_menu import option_menu
import utils  # Import helpers from utils.py


# No config import needed here unless using constants directly

# --- Specific Helper Function(s) for this Tab ---

def display_pump_status(pump_index):
    """Displays status metrics for a single circulation pump, showing status description."""
    st.subheader(f"Circulation Pump {pump_index} Details")

    # Define the mapping from status code to description
    status_map = {
        0: "Inactive",
        1: "Active (No Speed)",
        2: "Active (Speed Reached)",
        3: "Maintenance Req.",  # Shortened for space
        4: "Not Installed",
        5: "Insufficient Energy"
    }

    # Use a container for better visual separation of pump details
    with st.container(border=True):
        cols = st.columns(3)
        with cols[0]:
            # --- Fetch and display Pump Status Description ---
            status_code_var = f"COOLANT_CORE_CIRCULATION_PUMP_{pump_index}_STATUS"
            status_code_val = utils.fetch_variable_value(status_code_var)
            status_description = "Unknown"  # Default
            status_delta = None  # No delta for description metric

            if isinstance(status_code_val, (int, float)):
                # Convert float to int for dictionary lookup
                status_code_int = int(status_code_val)
                status_description = status_map.get(status_code_int, f"Unknown Code ({status_code_int})")
            elif isinstance(status_code_val, str) and "Error:" in status_code_val:
                status_description = "N/A"
                status_delta = status_code_val  # Show error in delta

            # Display the description using st.metric
            st.metric(label=f"Pump {pump_index} Status", value=status_description, delta=status_delta,
                      delta_color="off")
            # Removed the caption with the key

            # --- Display other metrics ---
            utils.display_metric(f"Pump {pump_index} Dry Status",
                                 f"COOLANT_CORE_CIRCULATION_PUMP_{pump_index}_DRY_STATUS",
                                 help_text="1: Active without fluid, 4: Inactive or OK")
            utils.display_metric(f"Pump {pump_index} Overload",
                                 f"COOLANT_CORE_CIRCULATION_PUMP_{pump_index}_OVERLOAD_STATUS",
                                 help_text="1: Active & Overload, 4: Inactive or OK")
        with cols[1]:
            utils.display_metric(f"Pump {pump_index} Speed (Actual)",
                                 f"COOLANT_CORE_CIRCULATION_PUMP_{pump_index}_SPEED")
        with cols[2]:
            utils.display_metric(f"Pump {pump_index} Speed (Ordered)",
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
            # Add caption for max pressure if needed, or rely on gauge axis
            # st.caption(f"Max: {utils.fetch_variable_value('COOLANT_CORE_MAX_PRESSURE')}")
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

    # --- Display details for ALL pumps (2, 1, 0) regardless of reported quantity ---
    st.subheader("Circulation Pump Details")  # Simplified subheader

    # Loop from 2 down to 0
    for i in range(2, -1, -1):
        display_pump_status(i)
        # Add a smaller divider between pumps if desired and not the last one
        if i > 0:
            st.divider()  # Optional divider between pumps
