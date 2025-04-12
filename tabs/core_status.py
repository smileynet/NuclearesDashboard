# tabs/core_status.py
import streamlit as st

import utils  # Import helpers from utils.py


def display_tab():
    st.header("Reactor Core Status")
    # Use columns for Temp and Pressure gauges side-by-side
    gauge_cols = st.columns(2)
    with gauge_cols[0]:
        utils.display_gauge(
            title="Core Temperature", value_var="CORE_TEMP",
            range_min_input="CORE_TEMP_MIN", range_max_input="CORE_TEMP_MAX",
            op_min_input="CORE_TEMP_OPERATIVE", op_max_input="CORE_TEMP_MAX",
            unit="°C"
        )
    with gauge_cols[1]:
        utils.display_gauge(
            title="Core Pressure", value_var="CORE_PRESSURE",
            range_min_input=0, range_max_input="CORE_PRESSURE_MAX",
            op_max_input="CORE_PRESSURE_OPERATIVE",
            unit="bar"
        )

    st.divider()
    # --- Other Core Metrics ---
    other_core_cols = st.columns(3)
    with other_core_cols[0]:
        utils.display_metric("Core State Code", "CORE_STATE")
        utils.display_metric("Core State Criticality", "CORE_STATE_CRITICALITY")
    with other_core_cols[1]:
        utils.display_metric("Critical Mass Reached?", "CORE_CRITICAL_MASS_REACHED")
    with other_core_cols[2]:
        utils.display_metric("Imminent Fusion?", "CORE_IMMINENT_FUSION")
        utils.display_metric("Ready for Start?", "CORE_READY_FOR_START")

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
        utils.display_metric("Rods Status Code", "RODS_STATUS")
        utils.display_metric("Rods Quantity", "RODS_QUANTITY")
    with cols_rods[1]:
        utils.display_metric("Rods Pos (Actual)", "RODS_POS_ACTUAL")
        utils.display_metric("Rods Pos (Ordered)", "RODS_POS_ORDERED")
    with cols_rods[2]:
        utils.display_metric("Rods Movement Speed", "RODS_MOVEMENT_SPEED")
        utils.display_metric("Rods Temp (°C)", "RODS_TEMPERATURE")
        st.caption(
            f"Max Temp: {utils.fetch_variable_value('RODS_MAX_TEMPERATURE')}")  # Fetch directly if needed only here
    with cols_rods[3]:
        utils.display_metric("Rods Aligned?", "RODS_ALIGNED")
        utils.display_metric("Rods Deformed?", "RODS_DEFORMED")
