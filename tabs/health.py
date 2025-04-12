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
    # Use two columns: one for Core, one for Rods
    col_core, col_rods = st.columns(2)

    with col_core:
        # --- Use NEW Custom Indicator for Core ---
        utils.display_component_health_indicator(
            label="Core",
            wear_var="CORE_WEAR",
            integrity_var="CORE_INTEGRITY"
        )
        # --- Remove old Core gauges ---
        # utils.display_gauge(title="Integrity", ...)
        # utils.display_gauge(title="Wear", ...)

    with col_rods:
        # --- Keep existing Rod display (Temp Gauge + Boolean Status) ---
        # Could be replaced with a custom indicator if needed, e.g., if ROD_WEAR existed
        st.markdown("**Control Rods**")
        # Rod Temperature Gauge
        rod_max_temp_value = utils.fetch_variable_value("RODS_MAX_TEMPERATURE")
        op_max_rod_temp = None
        if isinstance(rod_max_temp_value, (int, float)) and rod_max_temp_value > 0:
            op_max_rod_temp = 0.8 * rod_max_temp_value  # Start of red zone at 80%

        utils.display_gauge(
            title="Temperature",
            value_var="RODS_TEMPERATURE",
            range_min_input=0,
            range_max_input="RODS_MAX_TEMPERATURE",
            op_max_input=op_max_rod_temp,  # Defines start of RED zone
            unit="°C"
        )
        st.caption("Gauge: Green=Normal, Red=High(>80% Max)")

        # Rod Deformed Status
        utils.display_boolean_status("Deformed?", "RODS_DEFORMED")
        # --- End Rod Display ---

    st.divider()

    # --- Resources Section ---
    st.subheader("Resources")
    with st.container(border=True):
        # Use columns to place Fuel Level next to other resource info/charts
        col_fuel, col_wear_info = st.columns(2)

        with col_fuel:
            st.markdown("**Fuel**")
            # --- Fuel Level Gauge ---
            fuel_variable = "FUEL_LEVEL_PERCENT"  # Placeholder
            utils.display_gauge(
                title="Level",
                value_var=fuel_variable,
                range_min_input=0, range_max_input=100,
                op_max_input=15,  # Set threshold for "Low Fuel" (Red below 15%) - Defines start of RED zone
                unit="%"
            )
            st.caption(f"Gauge: Red < 15% (Low), Green >= 15%. Uses placeholder variable: `{fuel_variable}`")

        with col_wear_info:
            st.markdown("**Other Component Wear**")
            st.info("""
                A comparative bar chart for wear across multiple components (Pumps, Turbines, etc.)
                is recommended here but requires specific variables for each component's wear level.

                Core wear is displayed under 'Component Health'.
            """)
            # Placeholder for future bar chart if data becomes available
            # wear_data = { ... }
            # if valid_wear_data:
            #     wear_df = pd.DataFrame(...)
            #     st.bar_chart(wear_df.set_index('Component'))


    st.divider()

    # --- Time Section ---
    st.subheader("Time")
    with st.container(border=True):
        # Use columns to place time metrics side-by-side
        col_time1, col_time2 = st.columns(2)
        with col_time1:
            utils.display_metric("Sim Time", "TIME")
        with col_time2:
            utils.display_metric("Timestamp", "TIME_STAMP")

    st.divider()

    # --- Future / Other Section ---
    st.subheader("Future / Other (Data Needed)")
    st.markdown("""
        * **Prestige/XP:** (Variables Needed - *Metrics*)
        * **Energy Demand:** (Variable Needed - *Metric/Chart*)
        * **Chemical Status (Boron, pH, Xenon):** (Variables Needed - *Metrics/Charts*)
        * **AO Status:** (Variables Needed - *Text/Indicators*)
        * **Alarms:** (Variables Needed - *Log/Indicators*)
        * **Safety Systems (Resistance Banks, etc.):** (Variables Needed - *Custom Indicators*)
    """)  # Added Safety Systems placeholder
