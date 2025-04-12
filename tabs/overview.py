# tabs/overview.py
import pandas as pd  # Import pandas for history check
import plotly.express as px  # Import Plotly for chart
import streamlit as st

import utils  # Import helpers from utils.py


def display_tab(total_kw):  # Accept total_kw passed from main.py
    """Displays the content for the Overview tab."""
    st.header("Plant Status Overview")

    # --- Key Performance Indicators ---
    with st.container(border=True):
        st.subheader("Performance")
        cols_kpi = st.columns(3)
        with cols_kpi[0]:
            # Display total power passed from main.py
            st.metric(label="Total Output", value=f"{total_kw:.2f} kW")
        with cols_kpi[1]:
            # Placeholder for Energy Demand vs Output (requires demand variable)
            st.metric(label="Demand vs Output", value="N/A")
            st.caption("(Requires Energy Demand variable)")
        with cols_kpi[2]:
            # Placeholder for Prestige/XP (requires variables)
            st.metric(label="Prestige / XP", value="N/A")
            st.caption("(Requires Prestige/XP variables)")

        # --- Total KW History Chart ---
        st.markdown("---")  # Separator
        st.markdown("**Total Output History**")
        # Check session state exists and is a DataFrame and not empty
        if ('total_kw_history' in st.session_state and
                isinstance(st.session_state.total_kw_history, pd.DataFrame) and
                not st.session_state.total_kw_history.empty):
            # Ensure Timestamp column exists before setting index
            if 'Timestamp' in st.session_state.total_kw_history.columns:
                chart_df = st.session_state.total_kw_history.set_index('Timestamp')
                # Ensure the target column exists
                if 'Total Output (kW)' in chart_df.columns:
                    fig = px.line(
                        chart_df, y='Total Output (kW)',
                        labels={'Timestamp': 'Time'}
                    )
                    fig.update_layout(
                        xaxis={"fixedrange": True}, yaxis={"fixedrange": True},  # Disable zoom
                        height=250  # Adjust height as needed
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.caption("Total KW data column not found.")
            else:
                st.caption("Timestamp data column not found.")
        else:
            st.caption("Collecting Total KW data for chart...")
        # --- End of Total KW History Chart ---

    # --- Core & Coolant Status ---
    with st.container(border=True):
        st.subheader("Core & Coolant")
        # Use 4 columns: Gauges first, then other metrics
        cols_core = st.columns(4)
        with cols_core[0]:
            # --- Core Temp Gauge ---
            core_max_temp_value = utils.fetch_variable_value("CORE_TEMP_MAX")
            op_max_temp_for_gauge = None
            if isinstance(core_max_temp_value, (int, float)):
                op_max_temp_for_gauge = 0.9 * core_max_temp_value  # Use 90% heuristic

            utils.display_gauge(
                title="Core Temp",  # Shortened Title for Overview
                value_var="CORE_TEMP",
                range_min_input="CORE_TEMP_MIN",
                range_max_input="CORE_TEMP_MAX",
                op_min_input="CORE_TEMP_OPERATIVE",
                op_max_input=op_max_temp_for_gauge,
                unit="°C"
            )
        with cols_core[1]:
            # --- Core Pressure Gauge ---
            utils.display_gauge(
                title="Core Pressure",  # Shortened Title for Overview
                value_var="CORE_PRESSURE",
                range_min_input=0,
                range_max_input="CORE_PRESSURE_MAX",
                op_max_input="CORE_PRESSURE_OPERATIVE",
                unit="bar"
            )
        with cols_core[2]:
            # Display state codes/criticality here
            utils.display_metric("Core State", "CORE_STATE")
            utils.display_metric("Criticality", "CORE_STATE_CRITICALITY")  # Shortened label
        with cols_core[3]:
            # Display coolant info here
            utils.display_metric("Coolant Flow", "COOLANT_CORE_FLOW_SPEED")
            utils.display_metric("Loop Level", "COOLANT_CORE_PRIMARY_LOOP_LEVEL")
        # Captions explaining gauge colors can be added here if needed, or rely on tooltips/docs

    # --- Health & Safety Status ---
    with st.container(border=True):
        st.subheader("Health & Safety")
        cols_health = st.columns(3)
        with cols_health[0]:
            # Use metrics for compactness in overview
            utils.display_metric("Core Integrity (%)", "CORE_INTEGRITY")
            utils.display_metric("Core Wear (%)", "CORE_WEAR")
        with cols_health[1]:
            # Key safety bools
            utils.display_boolean_status("Rods Deformed?", "RODS_DEFORMED")
            # Placeholder for alarms (requires alarm variables)
            st.markdown("**Alarms:** N/A")
            st.caption("(Requires Alarm variables)")
        with cols_health[2]:
            # Placeholder for Fuel (requires variable)
            st.metric(label="Fuel Level (%)", value="N/A")
            st.caption("(Requires Fuel variable)")

    # Add more sections as needed when other variables (Chem, AO) become available
