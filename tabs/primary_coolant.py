# tabs/primary_coolant.py
import streamlit as st

import utils


def display_pump_status(pump_index):
    """Displays status metrics for a single circulation pump."""
    # Use utils.display_metric and utils.fetch_variable_value
    st.subheader(f"Circulation Pump {pump_index}")
    cols = st.columns(3)
    with cols[0]:
        utils.display_metric(f"Pump {pump_index} Status Code", f"COOLANT_CORE_CIRCULATION_PUMP_{pump_index}_STATUS")
        st.caption(
            "0: Inactive, 1: Active (No Speed), 2: Active (Speed Reached), 3: Maint. Req., 4: Not Installed, 5: No Energy")
        utils.display_metric(f"Pump {pump_index} Dry Status", f"COOLANT_CORE_CIRCULATION_PUMP_{pump_index}_DRY_STATUS",
                             help_text="1: Active without fluid, 4: Inactive or OK")
        utils.display_metric(f"Pump {pump_index} Overload",
                             f"COOLANT_CORE_CIRCULATION_PUMP_{pump_index}_OVERLOAD_STATUS",
                             help_text="1: Active & Overload, 4: Inactive or OK")
    with cols[1]:
        utils.display_metric(f"Pump {pump_index} Speed (Actual)", f"COOLANT_CORE_CIRCULATION_PUMP_{pump_index}_SPEED")
    with cols[2]:
        utils.display_metric(f"Pump {pump_index} Speed (Ordered)",
                             f"COOLANT_CORE_CIRCULATION_PUMP_{pump_index}_ORDERED_SPEED")


def display_tab():
    st.header("Primary Coolant Circuit")
    cols = st.columns(3)
    with cols[0]:
        utils.display_metric("Coolant State Code", "COOLANT_CORE_STATE")
        utils.display_metric("Coolant Pressure", "COOLANT_CORE_PRESSURE")
        st.caption(f"Max: {utils.fetch_variable_value('COOLANT_CORE_MAX_PRESSURE')}")
    with cols[1]:
        utils.display_metric("Vessel Temp (°C)", "COOLANT_CORE_VESSEL_TEMPERATURE")
        utils.display_metric("Primary Loop Level", "COOLANT_CORE_PRIMARY_LOOP_LEVEL")
    with cols[2]:
        utils.display_metric("Quantity in Vessel", "COOLANT_CORE_QUANTITY_IN_VESSEL")
        utils.display_metric("Flow Speed (Actual)", "COOLANT_CORE_FLOW_SPEED")
        st.caption(f"Ordered: {utils.fetch_variable_value('COOLANT_CORE_FLOW_ORDERED_SPEED')}")
    st.divider()

    num_pumps = utils.fetch_variable_value("COOLANT_CORE_QUANTITY_CIRCULATION_PUMPS_PRESENT")
    if isinstance(num_pumps, (int, float)) and num_pumps >= 0:
        for i in range(int(num_pumps)):
            display_pump_status(i)  # Call local helper
            st.divider()
    else:
        st.warning(f"Could not determine number of pumps or invalid value: {num_pumps}")
