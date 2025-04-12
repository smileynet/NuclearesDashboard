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
            st.markdown("**Core**")
            # --- Core Integrity Gauge ---
            utils.display_gauge(
                title="Integrity",
                value_var="CORE_INTEGRITY",
                range_min_input=0, range_max_input=100,
                op_max_input=70,  # Threshold for color split (higher is better)
                unit="%"
            )
            st.caption("Gauge: Red < 70%, Green >= 70%")

            # --- Core Wear Gauge ---
            utils.display_gauge(
                title="Wear",
                value_var="CORE_WEAR",
                range_min_input=0, range_max_input=100,
                op_max_input=30,  # Threshold for color split (higher is worse)
                unit="%"
            )
            st.caption("Gauge: Green < 30%, Red >= 30%")

        with col_rods:
            st.markdown("**Control Rods**")
            # --- Rod Temperature Gauge ---
            rod_max_temp_value = utils.fetch_variable_value("RODS_MAX_TEMPERATURE")
            op_max_rod_temp = None
            if isinstance(rod_max_temp_value, (int, float)) and rod_max_temp_value > 0:
                op_max_rod_temp = 0.8 * rod_max_temp_value  # Start of red zone at 80%

            utils.display_gauge(
                title="Temperature",
                value_var="RODS_TEMPERATURE",
                range_min_input=0,
                range_max_input="RODS_MAX_TEMPERATURE",
                op_max_input=op_max_rod_temp,
                unit="°C"
            )
            st.caption("Gauge: Green=Normal, Red=High(>80% Max)")

            # --- Rod Deformed Status ---
            utils.display_boolean_status("Deformed?", "RODS_DEFORMED")

    st.divider()

    # --- Resources Section ---
    st.subheader("Resources")
    with st.container(border=True):
        col_fuel, col_wear_info = st.columns(2)

        with col_fuel:
            st.markdown("**Fuel**")
            # --- Fuel Level Gauge ---
            # NOTE: Using placeholder variable "FUEL_LEVEL_PERCENT". Replace if actual variable is known.
            fuel_variable = "FUEL_LEVEL_PERCENT"  # Placeholder
            utils.display_gauge(
                title="Level",
                value_var=fuel_variable,
                range_min_input=0, range_max_input=100,
                op_max_input=15,  # Set threshold for "Low Fuel" (Red below 15%)
                unit="%"
            )
            st.caption(f"Gauge: Red < 15% (Low), Green >= 15%. Uses placeholder variable: `{fuel_variable}`")

        with col_wear_info:
            st.markdown("**Other Component Wear**")
            st.info("""
                A comparative bar chart for wear across multiple components (Pumps, Turbines, etc.)
                is recommended but requires specific variables for each component's wear level,
                which are not currently defined in `config.py`.

                Core wear is displayed under 'Component Health'.
            """)
            # Placeholder for future bar chart if data becomes available
            # Example structure (requires wear data):
            # wear_data = {
            #     'Pump 0': utils.fetch_variable_value("PUMP_0_WEAR_PLACEHOLDER"),
            #     'Pump 1': utils.fetch_variable_value("PUMP_1_WEAR_PLACEHOLDER"),
            #     'Turbine 0': utils.fetch_variable_value("TURBINE_0_WEAR_PLACEHOLDER"),
            # }
            # # Filter out errors and convert to DataFrame for charting
            # valid_wear_data = {k: v for k, v in wear_data.items() if isinstance(v, (int, float))}
            # if valid_wear_data:
            #     wear_df = pd.DataFrame(list(valid_wear_data.items()), columns=['Component', 'Wear (%)'])
            #     st.bar_chart(wear_df.set_index('Component'))
            # else:
            #     st.caption("Wear data for specific components unavailable.")

    st.divider()

    # --- Time Section ---
    st.subheader("Time")
    with st.container(border=True):
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
    """)  # Removed Fuel and Wear from this list
