# tabs/power_gen.py
import streamlit as st

import utils  # Import helpers from utils.py


# --- Specific Helper Function(s) for this Tab ---

def display_turbine_status(turbine_index):
    """Displays status metrics for a single steam turbine using gauges."""
    with st.container(border=True):
        st.markdown(f"**Steam Turbine {turbine_index}**")
        cols = st.columns(3)
        with cols[0]:
            # --- RPM Gauge ---
            utils.display_gauge(
                title="RPM",
                value_var=f"STEAM_TURBINE_{turbine_index}_RPM",
                range_min_input=0, range_max_input=4000,  # Assumed Max RPM
                op_min_input=1500, op_max_input=3800,  # Assumed operative range
                unit=""
            )
        with cols[1]:
            # --- Temperature Gauge ---
            utils.display_gauge(
                title="Temperature",
                value_var=f"STEAM_TURBINE_{turbine_index}_TEMPERATURE",
                range_min_input=0, range_max_input=600,  # Assumed Max Temp C
                op_min_input=100, op_max_input=550,  # Assumed operative range
                unit="°C"
            )
        with cols[2]:
            # --- Pressure Gauge ---
            utils.display_gauge(
                title="Pressure",
                value_var=f"STEAM_TURBINE_{turbine_index}_PRESSURE",
                range_min_input=0, range_max_input=100,  # Assumed Max Pressure (bar)
                op_max_input=80,  # Assumed start of 'high pressure' zone
                unit="bar"
            )

def display_generator_status(gen_index):
    """
    Displays status metrics for a single generator using gauges and icons.
    Uses a 2x2 grid layout for better visual balance.
    """
    with st.container(border=True):
        st.markdown(f"**Generator {gen_index}**")

        # --- Create a 2x2 Grid Layout ---
        row1_col1, row1_col2 = st.columns(2)
        row2_col1, row2_col2 = st.columns(2)

        # --- Row 1 ---
        with row1_col1:
            # Output Metric
            utils.display_metric(f"Output (kW)", f"GENERATOR_{gen_index}_KW")
            # Breaker Status
            breaker_val = utils.fetch_variable_value(f"GENERATOR_{gen_index}_BREAKER")
            if isinstance(breaker_val, bool):
                if breaker_val:  # True = Open
                    status_icon = "⚪"
                    status_text = "Open"
                    status_color = "grey"
                else:  # False = Closed
                    status_icon = "🟢"
                    status_text = "Closed"
                    status_color = "mediumseagreen"
                # Display Breaker status below the kW metric
                st.markdown(f"""
                <div style="display: flex; align-items: center; margin-top: 15px;">
                    <span style="font-weight: bold; margin-right: 8px;">Breaker:</span>
                    <span style="font-size: 1.2em; color: {status_color}; margin-right: 4px;">{status_icon}</span>
                    <span>{status_text}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Show error if fetching failed for breaker
                st.markdown(f"""
                 <div style="display: flex; align-items: center; margin-top: 15px;">
                     <span style="font-weight: bold; margin-right: 8px;">Breaker:</span>
                     <small>N/A ({utils.fetch_variable_value(f"GENERATOR_{gen_index}_BREAKER")})</small>
                 </div>
                 """, unsafe_allow_html=True)

        with row1_col2:
            # Voltage Gauge
            utils.display_gauge(
                title="Voltage", value_var=f"GENERATOR_{gen_index}_V",
                range_min_input=20000, range_max_input=30000,  # Assumed 20kV-30kV range
                op_min_input=24500, op_max_input=25500,  # Assumed +/- 2% of 25kV
                unit="V"
            )

        # --- Row 2 ---
        with row2_col1:
            # Frequency Gauge
            utils.display_gauge(
                title="Frequency", value_var=f"GENERATOR_{gen_index}_HERTZ",
                range_min_input=45, range_max_input=65,  # Assumed range around 50/60 Hz
                op_min_input=49.5, op_max_input=50.5,  # Assumed tight operative range
                unit="Hz"
            )

        with row2_col2:
            # Current Gauge
            utils.display_gauge(
                title="Current", value_var=f"GENERATOR_{gen_index}_A",
                range_min_input=0, range_max_input=1000,  # Assumed Max Amps
                op_max_input=900,  # Assumed start of high current zone
                unit="A"
            )


# --- Helper for Status Icons ---
def get_device_status_indicator(device_type, index):
    """ Determines a status icon based on fetched values. """
    icon = "⚪"  # Default: Unknown / Off / Open Breaker
    tooltip = "Status Unknown or Off"

    try:
        if device_type == "Turbine":
            rpm_val = utils.fetch_variable_value(f"STEAM_TURBINE_{index}_RPM")
            if isinstance(rpm_val, (int, float)):
                if rpm_val > 10:
                    icon, tooltip = "🟢", f"Active ({rpm_val:.0f} RPM)"
                else:
                    icon, tooltip = "🟡", f"Inactive ({rpm_val:.0f} RPM)"
            elif "Error:" in str(rpm_val):
                icon, tooltip = "🔴", f"Error fetching RPM: {rpm_val}"

        elif device_type == "Generator":
            kw_val = utils.fetch_variable_value(f"GENERATOR_{index}_KW")
            breaker_val = utils.fetch_variable_value(f"GENERATOR_{index}_BREAKER")

            if isinstance(kw_val, (int, float)) and isinstance(breaker_val, bool):
                if kw_val > 0 and not breaker_val:
                    icon, tooltip = "🟢", f"Active ({kw_val:.1f} kW, Breaker Closed)"
                elif kw_val <= 0 and not breaker_val:
                    icon, tooltip = "🟡", f"Inactive ({kw_val:.1f} kW, Breaker Closed)"
                elif breaker_val:
                    icon, tooltip = "⚪", f"Breaker Open ({kw_val:.1f} kW)"
            elif "Error:" in str(kw_val) or "Error:" in str(breaker_val):
                icon, tooltip = "🔴", f"Error fetching status (KW: {kw_val}, Breaker: {breaker_val})"
            elif kw_val == 0 and breaker_val:
                icon, tooltip = "⚪", "Off (Breaker Open)"

    except Exception as e:
        icon, tooltip = "🔴", f"Error checking status: {e}"

    return icon, tooltip

# --- Main Display Function for the Tab ---

def display_tab():
    """Displays the content for the Steam & Power Generation tab using expanders."""
    st.header("Steam & Power Generation")

    # --- Calculate and Display Total Power First ---
    total_kw = 0.0
    active_generators = 0
    for i in range(3):
        kw_value = utils.fetch_variable_value(f"GENERATOR_{i}_KW")
        if isinstance(kw_value, float):
            breaker_val = utils.fetch_variable_value(f"GENERATOR_{i}_BREAKER")
            if isinstance(breaker_val, bool) and not breaker_val:  # Count power only if breaker is closed
                total_kw += kw_value
                if kw_value > 0: active_generators += 1

    st.metric(label="Total Generator Output", value=f"{total_kw:.2f} kW",
              delta=f"{active_generators} Active Generator(s)")
    st.divider()
    # --- End of Total Power Display ---

    # --- Device Status Overview Section ---
    with st.container(border=True):
        st.subheader("Device Status Overview")
        cols = st.columns(6)  # 3 turbines + 3 generators
        device_pairs = [("Turbine", 0), ("Generator", 0),
                        ("Turbine", 1), ("Generator", 1),
                        ("Turbine", 2), ("Generator", 2)]
        for idx, (dev_type, dev_index) in enumerate(device_pairs):
            with cols[idx]:
                icon, tooltip = get_device_status_indicator(dev_type, dev_index)
                st.markdown(f"""
                <div style="text-align: center;" title="{tooltip}">
                    <span style="font-size: 1.8em;">{icon}</span><br>
                    <span style="font-size: 0.9em;">{dev_type} {dev_index}</span>
                </div>
                """, unsafe_allow_html=True)
        st.caption("""
            **Status Key:** 🟢 Active | 🟡 Idle/Inactive (Connected) | ⚪ Off / Breaker Open | 🔴 Error/Unknown
        """)
    # --- End of Device Status Overview ---

    st.divider()

    # --- Turbines & Steam Expander ---
    with st.expander("**Turbines & Steam**", expanded=True):
        st.subheader("Steam Presence")
        with st.container(border=True):  # Keep border for this section
            cols_steam = st.columns(2)
            with cols_steam[0]:
                utils.display_metric("Steam Present?", "CORE_STEAM_PRESENT")
            with cols_steam[1]:
                utils.display_metric("High Steam Present?", "CORE_HIGH_STEAM_PRESENT")

        st.divider()  # Divider within the expander

        st.subheader("Turbine Details")
        turbine_active_count = 0
        for i in range(3):
            rpm_value = utils.fetch_variable_value(f"STEAM_TURBINE_{i}_RPM")
            # Check if data is valid before displaying
            if not (isinstance(rpm_value, str) and "Error:" in rpm_value):
                display_turbine_status(i)
                turbine_active_count += 1
                st.markdown("<br>", unsafe_allow_html=True)  # Add space

        if turbine_active_count == 0:
            st.caption("No active turbines detected or data unavailable.")

    st.divider()  # Divider between expanders

    # --- Generators Expander ---
    with st.expander("**Generators**", expanded=True):
        st.subheader("Generator Details")
        generator_active_count = 0
        for i in range(3):
            kw_value = utils.fetch_variable_value(f"GENERATOR_{i}_KW")
            # Check if data is valid before displaying
            if not (isinstance(kw_value, str) and "Error:" in kw_value):
                # Call the updated display function with the 2x2 grid
                display_generator_status(i)
                generator_active_count += 1
                st.markdown("<br>", unsafe_allow_html=True)  # Add space

        if generator_active_count == 0:
            st.caption("No active generators detected or data unavailable.")
