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
        # Use columns to place related KPIs side-by-side
        cols_kpi_row1 = st.columns(3)
        with cols_kpi_row1[0]:
            # Display total power passed from main.py, now including the delta
            st.metric(label="Total Output", value=f"{total_kw:.2f} kW", delta=total_kw_delta)
        with cols_kpi_row1[1]:
            # Placeholder - When demand variable exists, place next to output
            # demand_value = utils.fetch_variable_value("ENERGY_DEMAND") # Example fetch
            # st.metric(label="Energy Demand", value=f"{demand_value} kW") # Example display
            st.metric(label="Energy Demand", value="N/A")  # Current placeholder
            st.caption("(Requires Energy Demand variable)")
        with cols_kpi_row1[2]:
            # Placeholder for Prestige/XP (requires variables)
            st.metric(label="Prestige / XP", value="N/A")
            st.caption("(Requires Prestige/XP variables)")

        # Example placeholder for a second row of KPIs comparing charts/metrics
        # st.markdown("---")
        # cols_kpi_row2 = st.columns(2)
        # with cols_kpi_row2[0]:
        #    # Display Demand vs Supply Chart here when data is available
        #    st.caption("Demand vs Supply Chart (placeholder)")
        #    # Example:
        #    # if 'demand_supply_history' in st.session_state and not st.session_state.demand_supply_history.empty:
        #    #     st.line_chart(st.session_state.demand_supply_history.set_index('Timestamp'))
        #    # else:
        #    #     st.caption("Collecting Demand/Supply data...")
        # with cols_kpi_row2[1]:
        #    # Example: Place fuel consumption rate next to demand/supply chart
        #    # utils.display_metric("Fuel Consumption Rate", "FUEL_CONSUMPTION_RATE_PLACEHOLDER") # Placeholder variable
        #    st.caption("Fuel Consumption Metric (placeholder)")


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
        # Use columns to place Core Temp and Pressure gauges side-by-side
        cols_core = st.columns(4)  # Keep 4 columns for overall layout balance
        with cols_core[0]:
            # Core Temp Gauge
            core_max_temp_value = utils.fetch_variable_value("CORE_TEMP_MAX")
            op_max_temp_for_gauge = None
            if isinstance(core_max_temp_value, (int, float)): op_max_temp_for_gauge = 0.9 * core_max_temp_value
            utils.display_gauge(
                title="Core Temp", value_var="CORE_TEMP", range_min_input="CORE_TEMP_MIN",
                range_max_input="CORE_TEMP_MAX", op_min_input="CORE_TEMP_OPERATIVE",
                op_max_input=op_max_temp_for_gauge, unit="°C"
            )
        with cols_core[1]:
            # Core Pressure Gauge - Placed next to Core Temp gauge
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
        # Use columns to pair related health metrics
        cols_health = st.columns(3)
        with cols_health[0]:
            # Core Integrity and Wear together
            utils.display_metric("Core Integrity (%)", "CORE_INTEGRITY")
            utils.display_metric("Core Wear (%)", "CORE_WEAR")
        with cols_health[1]:
            # Rod Status and Alarms together
            utils.display_boolean_status("Rods Deformed?", "RODS_DEFORMED")
            st.markdown("**Alarms:** N/A")  # Placeholder for alarm summary/indicator
            st.caption("(Requires Alarm variables)")
        with cols_health[2]:
            # Fuel Status
            # Example using display_metric if a numeric fuel variable exists
            # utils.display_metric("Fuel Level (%)", "FUEL_LEVEL_PERCENT_PLACEHOLDER") # Placeholder variable
            st.metric(label="Fuel Level (%)", value="N/A")  # Current placeholder
            st.caption("(Requires Fuel variable)")
