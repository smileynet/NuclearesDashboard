# tabs/core_status.py
import plotly.express as px  # Import Plotly Express for charts
import streamlit as st

import utils  # Import helpers from utils.py


# --- Main Display Function for the Tab ---

def display_tab():
    """Displays the content for the Core Status tab."""
    st.header("Reactor Core Status")
    # Use columns for Temp and Pressure gauges side-by-side
    gauge_cols = st.columns(2)
    with gauge_cols[0]:
        # --- Core Temp Gauge ---
        utils.display_gauge(
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
        utils.display_gauge(
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
        utils.display_metric("Core State Code", "CORE_STATE")
        utils.display_metric("Core State Criticality", "CORE_STATE_CRITICALITY")
    with other_core_cols[1]:
        utils.display_metric("Critical Mass Reached?", "CORE_CRITICAL_MASS_REACHED")
    with other_core_cols[2]:
        utils.display_metric("Imminent Fusion?", "CORE_IMMINENT_FUSION")
        utils.display_metric("Ready for Start?", "CORE_READY_FOR_START")

    st.divider()
    # --- Core Temp History Chart (using Plotly) ---
    st.subheader("Core Temperature History")
    if 'core_temp_history' in st.session_state and not st.session_state.core_temp_history.empty:
        # Prepare DataFrame (Timestamp likely already index from previous code)
        # Ensure Timestamp is the index for Plotly Express
        chart_df = st.session_state.core_temp_history.set_index('Timestamp')

        # Create Plotly figure using Plotly Express
        fig = px.line(
            chart_df,
            y='Core Temp (°C)',  # Specify the column for the y-axis
            # title="Core Temperature Trend" # Title can be omitted if subheader is sufficient
            labels={'Timestamp': 'Time'}  # Optional: Rename axes
        )

        # --- Disable Zooming ---
        # Set fixedrange to True for both axes to disable zoom
        fig.update_layout(
            xaxis={"fixedrange": True},
            yaxis={"fixedrange": True},
            height=300  # Optional: Adjust height
        )

        # Display using st.plotly_chart
        st.plotly_chart(fig, use_container_width=True)
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
        # Fetch max temp directly if needed only here for caption
        st.caption(f"Max Temp: {utils.fetch_variable_value('RODS_MAX_TEMPERATURE')}")
    with cols_rods[3]:
        utils.display_metric("Rods Aligned?", "RODS_ALIGNED")
        utils.display_metric("Rods Deformed?", "RODS_DEFORMED")

