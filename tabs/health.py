# tabs/health.py
import streamlit as st

import utils  # Import helpers from utils.py


# No need to import config here unless specific constants are needed directly

# --- Main Display Function for the Tab ---

def display_tab():
    """Displays the content for the Plant Health & Resources tab."""
    st.header("Plant Health & Resources")

    # Use columns for layout
    health_cols = st.columns(3)
    with health_cols[0]:
        st.subheader("Core Health")
        # Use generic gauge display from utils
        utils.display_gauge(
            title="Core Integrity",
            value_var="CORE_INTEGRITY",
            range_min_input=0, range_max_input=100,  # Assuming 0-100 range
            unit="%"
        )
        utils.display_gauge(
            title="Core Wear",
            value_var="CORE_WEAR",
            range_min_input=0, range_max_input=100,
            unit="%"
        )
    with health_cols[1]:
        st.subheader("Rod Health")
        # Use generic metric display from utils
        utils.display_metric("Rods Temp (°C)", "RODS_TEMPERATURE")
        # Fetch max temp directly if needed only here for caption
        st.caption(f"Max Temp: {utils.fetch_variable_value('RODS_MAX_TEMPERATURE')}")
        utils.display_metric("Rods Deformed?", "RODS_DEFORMED")
    with health_cols[2]:
        st.subheader("Time")
        # Use generic metric display from utils
        utils.display_metric("Sim Time", "TIME")
        utils.display_metric("Timestamp", "TIME_STAMP")

    st.divider()

    # Placeholder section for missing variables
    st.subheader("Future / Other")
    st.markdown("""
        * **Fuel Level:** (Variable Needed - *Good candidate for Gauge*)
        * **Component Wear (Pumps, Turbines):** (Variables Needed - *Gauges?*)
        * **Prestige/XP:** (Variables Needed - *Metrics*)
        * **Energy Demand:** (Variable Needed - *Metric/Chart*)
        * **Chemical Status (Boron, pH, Xenon):** (Variables Needed - *Metrics/Charts*)
        * **AO Status:** (Variables Needed - *Text/Indicators*)
    """)
