# tabs/core_status.py
import pandas as pd  # <--- ADDED IMPORT
import plotly.express as px  # Import Plotly Express for charts
import streamlit as st

import utils  # Import helpers from utils.py


# --- Main Display Function for the Tab ---

def display_tab():
    """Displays the content for the Core Status tab."""
    st.header("Reactor Core Status")

    # --- Gauges Section ---
    with st.container(border=True):
        st.subheader("Core Conditions")
        gauge_cols = st.columns(2)
        with gauge_cols[0]:
            # Core Temp Gauge
            utils.display_gauge(
                title="Core Temperature", value_var="CORE_TEMP",
                # Use explicit variable names for clarity
                range_min_input="CORE_TEMP_MIN",
                range_max_input="CORE_TEMP_MAX",
                op_min_input="CORE_TEMP_OPERATIVE",  # Defines start of green zone
                # Calculate op_max cleanly before the call
                op_max_input=0.9 * utils.fetch_variable_value("CORE_TEMP_MAX") if isinstance(
                    utils.fetch_variable_value("CORE_TEMP_MAX"), (int, float)) else None,
                unit="°C"
            )
        with gauge_cols[1]:
            # Core Pressure Gauge
            utils.display_gauge(
                title="Core Pressure", value_var="CORE_PRESSURE",
                range_min_input=0,  # Use 0 directly
                range_max_input="CORE_PRESSURE_MAX",
                op_max_input="CORE_PRESSURE_OPERATIVE",  # Defines start of red zone
                unit="bar"
            )
        # Add Caption explaining colors
        st.caption("""
            **Gauge Colors:** Temp: Blue=Cold, Green=Operative, Red=Hot. Pressure: Green=Normal, Red=High.
            Red line indicates start of Hot/High zone.
        """)

    # --- Other Core Metrics Section ---
    with st.container(border=True):
        st.subheader("Core State")
        other_core_cols = st.columns(3)
        with other_core_cols[0]:
            utils.display_metric("State Code", "CORE_STATE")  # Shortened label
            utils.display_metric("State Criticality", "CORE_STATE_CRITICALITY")
        with other_core_cols[1]:
            # Use new boolean status display
            utils.display_boolean_status("Critical Mass?", "CORE_CRITICAL_MASS_REACHED")
            utils.display_boolean_status("Imminent Fusion?", "CORE_IMMINENT_FUSION")
        with other_core_cols[2]:
            utils.display_boolean_status("Ready for Start?", "CORE_READY_FOR_START")

    # --- History Chart Section (in Expander) ---
    with st.expander("Core Temperature History", expanded=True):  # Start expanded
        # Check session state exists and is a DataFrame and not empty
        # Now 'pd' is defined because of the import added above
        if ('core_temp_history' in st.session_state and
                isinstance(st.session_state.core_temp_history, pd.DataFrame) and
                not st.session_state.core_temp_history.empty):
            # Ensure Timestamp column exists before setting index
            if 'Timestamp' in st.session_state.core_temp_history.columns:
                chart_df = st.session_state.core_temp_history.set_index('Timestamp')
                # Ensure the target column exists
                if 'Core Temp (°C)' in chart_df.columns:
                    fig = px.line(
                        chart_df, y='Core Temp (°C)',
                        labels={'Timestamp': 'Time'}
                    )
                    fig.update_layout(
                        xaxis={"fixedrange": True}, yaxis={"fixedrange": True},
                        height=300
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.caption("Temperature data column not found.")
            else:
                st.caption("Timestamp data column not found.")
        else:
            st.caption("Collecting temperature data for chart...")


    # --- Control Rods Section ---
    with st.container(border=True):
        st.subheader("Control Rods")
        cols_rods_1 = st.columns(4)  # First row of rod info
        with cols_rods_1[0]:
            utils.display_metric("Status Code", "RODS_STATUS")
            utils.display_metric("Quantity", "RODS_QUANTITY")
        with cols_rods_1[1]:
            utils.display_metric("Pos (Actual)", "RODS_POS_ACTUAL")
            utils.display_metric("Pos (Ordered)", "RODS_POS_ORDERED")
        with cols_rods_1[2]:
            utils.display_metric("Movement Speed", "RODS_MOVEMENT_SPEED")
            utils.display_boolean_status("Aligned?", "RODS_ALIGNED")
        with cols_rods_1[3]:
            utils.display_boolean_status("Deformed?", "RODS_DEFORMED")

        st.divider()  # Separator before rod temp gauge

        # --- Rod Temperature Gauge ---
        # Fetch max temp first to calculate op_max cleanly
        rod_max_temp_value = utils.fetch_variable_value("RODS_MAX_TEMPERATURE")
        op_max_rod_temp = None  # Default to None
        # Check if max temp is valid number before calculation
        if isinstance(rod_max_temp_value, (int, float)) and rod_max_temp_value > 0:
            op_max_rod_temp = 0.8 * rod_max_temp_value  # Start of red zone at 80%

        # Call the gauge function
        utils.display_gauge(
            title="Rod Temperature",
            value_var="RODS_TEMPERATURE",
            range_min_input=0,  # Assuming min temp is 0
            range_max_input="RODS_MAX_TEMPERATURE",  # Still pass var name for max range
            op_max_input=op_max_rod_temp,  # Pass the calculated value (or None)
            unit="°C"
        )
        st.caption("Rod Temp Gauge: Green = Normal, Red = High (>80% Max). Red line indicates threshold.")
