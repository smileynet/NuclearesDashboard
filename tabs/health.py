# tabs/health.py
import streamlit as st

import utils  # Import helpers from utils.py


# No config import needed here unless using constants directly

# --- Main Display Function for the Tab ---

def display_tab():
    """Displays the content for the Plant Health & Resources tab with consolidated layout."""
    st.header("Plant Health & Resources")

    # --- Consolidated Component Health Section ---
    st.subheader("Component Health")
    with st.container(border=True):
        # Use two columns: one for Core, one for Rods
        col_core, col_rods = st.columns(2)

        with col_core:
            st.markdown("**Core**")  # Sub-heading for Core
            # --- Core Integrity Gauge ---
            # Refined: Set threshold for Red/Green split at 70
            # Values below 70 will be Red, above will be Green
            utils.display_gauge(
                title="Integrity",  # Shortened title
                value_var="CORE_INTEGRITY",
                range_min_input=0, range_max_input=100,
                op_max_input=70,  # Threshold for color split (higher is better)
                unit="%"
            )
            st.caption("Gauge: Red < 70%, Green >= 70%")

            # --- Core Wear Gauge ---
            # Refined: Set threshold for Green/Red split at 30
            # Values below 30 will be Green, above will be Red
            utils.display_gauge(
                title="Wear",  # Shortened title
                value_var="CORE_WEAR",
                range_min_input=0, range_max_input=100,
                op_max_input=30,  # Threshold for color split (higher is worse)
                unit="%"
            )
            st.caption("Gauge: Green < 30%, Red >= 30%")

        with col_rods:
            st.markdown("**Control Rods**")  # Sub-heading for Rods
            # --- Rod Temperature Gauge ---
            rod_max_temp_value = utils.fetch_variable_value("RODS_MAX_TEMPERATURE")
            op_max_rod_temp = None  # Default to None
            if isinstance(rod_max_temp_value, (int, float)) and rod_max_temp_value > 0:
                op_max_rod_temp = 0.8 * rod_max_temp_value  # Start of red zone at 80%

            # Call uses existing logic where op_max_input defines start of Red zone
            utils.display_gauge(
                title="Temperature",  # Shortened title
                value_var="RODS_TEMPERATURE",
                range_min_input=0,  # Assuming min temp is 0
                range_max_input="RODS_MAX_TEMPERATURE",
                op_max_input=op_max_rod_temp,  # Pass calculated threshold
                unit="°C"
            )
            st.caption("Gauge: Green=Normal, Red=High(>80% Max)")  # Specific caption

            # --- Rod Deformed Status ---
            utils.display_boolean_status("Deformed?", "RODS_DEFORMED")

    st.divider()

    # --- Time Section ---
    st.subheader("Time")
    with st.container(border=True):
        # Use columns to keep time metrics compact
        col_time1, col_time2 = st.columns(2)
        with col_time1:
            utils.display_metric("Sim Time", "TIME")
        with col_time2:
            utils.display_metric("Timestamp", "TIME_STAMP")

    st.divider()

    # --- Future / Other Section ---
    st.subheader("Future / Other (Data Needed)")
    st.markdown("""
        * **Fuel Level:** (Variable Needed - *Good candidate for Gauge*)
        * **Component Wear (Pumps, Turbines):** (Variables Needed - *Gauges?*)
        * **Prestige/XP:** (Variables Needed - *Metrics*)
        * **Energy Demand:** (Variable Needed - *Metric/Chart*)
        * **Chemical Status (Boron, pH, Xenon):** (Variables Needed - *Metrics/Charts*)
        * **AO Status:** (Variables Needed - *Text/Indicators*)
    """)
