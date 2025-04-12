# tabs/overview.py
import pandas as pd
import plotly.express as px
import streamlit as st

import utils  # Import helpers from utils.py


# --- UPDATED function signature to accept total_kw_delta ---
def display_tab(total_kw, total_kw_delta):
    """Displays the content for the Overview tab."""
    st.header("Plant Status Overview")

    # --- Key Performance Indicators ---
    with st.container(border=True):
        st.subheader("Performance")
        cols_kpi = st.columns(3)
        with cols_kpi[0]:
            # Display total power passed from main.py, now including the delta
            st.metric(label="Total Output", value=f"{total_kw:.2f} kW", delta=total_kw_delta)
        with cols_kpi[1]:
            # Placeholder for Energy Demand vs Output (requires demand variable)
            st.metric(label="Demand vs Output", value="N/A")
            st.caption("(Requires Energy Demand variable)")
        with cols_kpi[2]:
            # Placeholder for Prestige/XP (requires variables)
            st.metric(label="Prestige / XP", value="N/A")
            st.caption("(Requires Prestige/XP variables)")

        # --- Total KW History Chart ---
        st.markdown("---")
        st.markdown("**Total Output History**")
        if ('total_kw_history' in st.session_state and
                isinstance(st.session_state.total_kw_history, pd.DataFrame) and
                not st.session_state.total_kw_history.empty):
            if 'Timestamp' in st.session_state.total_kw_history.columns:
                chart_df = st.session_state.total_kw_history.set_index('Timestamp')
                if 'Total Output (kW)' in chart_df.columns:
                    fig = px.line(chart_df, y='Total Output (kW)', labels={'Timestamp': 'Time'})
                    fig.update_layout(xaxis={"fixedrange": True}, yaxis={"fixedrange": True}, height=250)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.caption("Total KW data column not found.")
            else:
                st.caption("Timestamp data column not found.")
        else:
            st.caption("Collecting Total KW data for chart...")

    # --- Core & Coolant Status ---
    with st.container(border=True):
        st.subheader("Core & Coolant")
        cols_core = st.columns(4)
        with cols_core[0]:
            # Core Temp Gauge (Delta handled by utils.display_metric if shown as metric)
            core_max_temp_value = utils.fetch_variable_value("CORE_TEMP_MAX")
            op_max_temp_for_gauge = None
            if isinstance(core_max_temp_value, (int, float)): op_max_temp_for_gauge = 0.9 * core_max_temp_value
            utils.display_gauge(
                title="Core Temp", value_var="CORE_TEMP", range_min_input="CORE_TEMP_MIN",
                range_max_input="CORE_TEMP_MAX", op_min_input="CORE_TEMP_OPERATIVE",
                op_max_input=op_max_temp_for_gauge, unit="°C"
            )
        with cols_core[1]:
            # Core Pressure Gauge
            utils.display_gauge(
                title="Core Pressure", value_var="CORE_PRESSURE", range_min_input=0,
                range_max_input="CORE_PRESSURE_MAX", op_max_input="CORE_PRESSURE_OPERATIVE", unit="bar"
            )
        with cols_core[2]:
            # These use utils.display_metric and will now show delta automatically
            utils.display_metric("Core State", "CORE_STATE")
            utils.display_metric("Criticality", "CORE_STATE_CRITICALITY")
        with cols_core[3]:
            # These use utils.display_metric and will now show delta automatically
            utils.display_metric("Coolant Flow", "COOLANT_CORE_FLOW_SPEED")
            utils.display_metric("Loop Level", "COOLANT_CORE_PRIMARY_LOOP_LEVEL")

    # --- Health & Safety Status ---
    with st.container(border=True):
        st.subheader("Health & Safety")
        cols_health = st.columns(3)
        with cols_health[0]:
            # These use utils.display_metric and will now show delta automatically
            utils.display_metric("Core Integrity (%)", "CORE_INTEGRITY")
            utils.display_metric("Core Wear (%)", "CORE_WEAR")
        with cols_health[1]:
            # Boolean status does not show delta
            utils.display_boolean_status("Rods Deformed?", "RODS_DEFORMED")
            st.markdown("**Alarms:** N/A")
            st.caption("(Requires Alarm variables)")
        with cols_health[2]:
            # Fuel Level uses gauge, but if shown as metric, delta would apply
            st.metric(label="Fuel Level (%)", value="N/A")  # Placeholder
            st.caption("(Requires Fuel variable)")

