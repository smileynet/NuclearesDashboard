# tabs/power_gen.py
import streamlit as st

import utils  # Import helpers from utils.py


# No config import needed here unless using constants directly

# --- Specific Helper Function(s) for this Tab ---

def display_turbine_status(turbine_index):
    """Displays status metrics for a single steam turbine using gauges."""
    with st.container(border=True):
        st.markdown(f"**Steam Turbine {turbine_index}**")  # Use markdown for bold title
        cols = st.columns(3)
        with cols[0]:
            # --- RPM Gauge ---
            # NOTE: Max RPM and operative ranges are assumed, adjust as needed.
            utils.display_gauge(
                title="RPM",
                value_var=f"STEAM_TURBINE_{turbine_index}_RPM",
                range_min_input=0,
                range_max_input=4000,  # Assumed Max RPM
                op_min_input=1500,  # Assumed start of operative range
                op_max_input=3800,  # Assumed end of operative range (start of red)
                unit=""  # Unit RPM is implied
            )
        with cols[1]:
            # --- Temperature Gauge ---
            # NOTE: Max Temp and operative ranges are assumed, adjust as needed.
            utils.display_gauge(
                title="Temperature",
                value_var=f"STEAM_TURBINE_{turbine_index}_TEMPERATURE",
                range_min_input=0,
                range_max_input=600,  # Assumed Max Temp C
                op_min_input=100,  # Assumed start of operative range
                op_max_input=550,  # Assumed start of 'hot' zone
                unit="°C"
            )
        with cols[2]:
            # --- Pressure Gauge ---
            # NOTE: Max Pressure and operative ranges are assumed, adjust as needed.
            utils.display_gauge(
                title="Pressure",
                value_var=f"STEAM_TURBINE_{turbine_index}_PRESSURE",
                range_min_input=0,
                range_max_input=100,  # Assumed Max Pressure (bar)
                # op_min_input=10, # Optional: Assumed min operative pressure
                op_max_input=80,  # Assumed start of 'high pressure' zone
                unit="bar"  # Assuming bar
            )
        # Add a common caption for assumptions if desired
        # st.caption("Note: Gauge ranges (Max, Operative) are estimates.")


def display_generator_status(gen_index):
    """Displays status metrics for a single generator using gauges and icons."""
    with st.container(border=True):
        st.markdown(f"**Generator {gen_index}**")  # Use markdown for bold title
        cols = st.columns(3)  # Use 3 columns for kW metric + 2 gauges
        with cols[0]:
            # Keep kW as a metric for clear visibility
            utils.display_metric(f"Output (kW)", f"GENERATOR_{gen_index}_KW")

            # --- Breaker Status (Icon/Text) ---
            breaker_val = utils.fetch_variable_value(f"GENERATOR_{gen_index}_BREAKER")
            if isinstance(breaker_val, bool):
                if breaker_val:  # True = Open
                    status_icon = "⚪"
                    status_text = "Open"
                    status_color = "grey"
                else:  # False = Closed
                    status_icon = "🟢"  # Use Green check variation maybe? Or a link icon? Let's use green dot.
                    status_text = "Closed"
                    status_color = "mediumseagreen"
                st.markdown(f"""
                <div style="display: flex; align-items: center; margin-top: 10px;">
                    <span style="font-weight: bold; margin-right: 8px;">Breaker:</span>
                    <span style="font-size: 1.2em; color: {status_color}; margin-right: 4px;">{status_icon}</span>
                    <span>{status_text}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Show error if fetching failed
                utils.display_metric(f"Breaker", f"GENERATOR_{gen_index}_BREAKER")

        with cols[1]:
            # --- Voltage Gauge ---
            # NOTE: Assumed ranges based on typical grid standards (e.g., around 25kV) - ADJUST AS NEEDED
            utils.display_gauge(
                title="Voltage", value_var=f"GENERATOR_{gen_index}_V",
                range_min_input=20000, range_max_input=30000,  # Assumed 20kV-30kV range
                op_min_input=24500, op_max_input=25500,  # Assumed +/- 2% of 25kV
                unit="V"
            )
            # --- Frequency Gauge ---
            # NOTE: Assumed ranges for grid frequency - ADJUST AS NEEDED
            utils.display_gauge(
                title="Frequency", value_var=f"GENERATOR_{gen_index}_HERTZ",
                range_min_input=45, range_max_input=65,  # Assumed range around 50/60 Hz
                op_min_input=49.5, op_max_input=50.5,  # Assumed tight operative range around 50Hz
                unit="Hz"
            )

        with cols[2]:
            # --- Current Gauge ---
            # NOTE: Assumed max current - ADJUST AS NEEDED
            utils.display_gauge(
                title="Current", value_var=f"GENERATOR_{gen_index}_A",
                range_min_input=0,
                range_max_input=1000,  # Assumed Max Amps (adjust significantly based on kW/V)
                op_max_input=900,  # Assumed start of high current zone (90% of max)
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
                if rpm_val > 10:  # Example threshold for 'active'
                    icon = "🟢"  # Green: Active
                    tooltip = f"Active ({rpm_val:.0f} RPM)"
                else:
                    icon = "🟡"  # Yellow: Inactive/Idle
                    tooltip = f"Inactive ({rpm_val:.0f} RPM)"
            elif "Error:" in str(rpm_val):
                icon = "🔴"  # Red: Error
                tooltip = f"Error fetching RPM: {rpm_val}"

        elif device_type == "Generator":
            kw_val = utils.fetch_variable_value(f"GENERATOR_{index}_KW")
            breaker_val = utils.fetch_variable_value(f"GENERATOR_{index}_BREAKER")

            if isinstance(kw_val, (int, float)) and isinstance(breaker_val, bool):
                if kw_val > 0 and not breaker_val:  # KW > 0 and Breaker CLOSED (False)
                    icon = "🟢"  # Green: Active & Connected
                    tooltip = f"Active ({kw_val:.1f} kW, Breaker Closed)"
                elif kw_val <= 0 and not breaker_val:
                    icon = "🟡"  # Yellow: Connected but Inactive
                    tooltip = f"Inactive ({kw_val:.1f} kW, Breaker Closed)"
                elif breaker_val:  # Breaker OPEN (True)
                    icon = "⚪"  # White/Grey: Breaker Open
                    tooltip = f"Breaker Open ({kw_val:.1f} kW)"
            # Check for errors after checking valid types
            elif "Error:" in str(kw_val) or "Error:" in str(breaker_val):
                icon = "🔴"  # Red: Error
                tooltip = f"Error fetching status (KW: {kw_val}, Breaker: {breaker_val})"
            # Handle cases where values might be valid type but still indicate off/unavailable
            elif kw_val == 0 and breaker_val:  # Explicitly off
                icon = "⚪"
                tooltip = "Off (Breaker Open)"


    except Exception as e:
        icon = "🔴"
        tooltip = f"Error checking status: {e}"

    return icon, tooltip

# --- Main Display Function for the Tab ---

def display_tab():
    """Displays the content for the Steam & Power Generation tab."""
    st.header("Steam & Power Generation")

    # --- Calculate and Display Total Power First ---
    total_kw = 0.0
    active_generators = 0
    for i in range(3):
        # Fetch KW value to sum up total power
        kw_value = utils.fetch_variable_value(f"GENERATOR_{i}_KW")
        if isinstance(kw_value, float):
            # Count power only if breaker is closed (False)
            breaker_val = utils.fetch_variable_value(f"GENERATOR_{i}_BREAKER")
            if isinstance(breaker_val, bool) and not breaker_val:
                total_kw += kw_value
                if kw_value > 0:  # Count as active if producing power AND connected
                    active_generators += 1

    # Display Total Power using st.metric for better visibility
    st.metric(label="Total Generator Output", value=f"{total_kw:.2f} kW",
              delta=f"{active_generators} Active Generator(s)")
    st.divider()
    # --- End of Total Power Display ---

    # --- Device Status Overview Section ---
    with st.container(border=True):
        st.subheader("Device Status Overview")
        # Create columns for each device status indicator
        cols = st.columns(6)  # 3 turbines + 3 generators

        device_pairs = [("Turbine", 0), ("Generator", 0),
                        ("Turbine", 1), ("Generator", 1),
                        ("Turbine", 2), ("Generator", 2)]

        for idx, (dev_type, dev_index) in enumerate(device_pairs):
            with cols[idx]:
                icon, tooltip = get_device_status_indicator(dev_type, dev_index)
                # Display centered icon and label
                st.markdown(f"""
                <div style="text-align: center;" title="{tooltip}">
                    <span style="font-size: 1.8em;">{icon}</span><br>
                    <span style="font-size: 0.9em;">{dev_type} {dev_index}</span>
                </div>
                """, unsafe_allow_html=True)

        # --- ADDED: Key for Status Icons ---
        st.caption("""
            **Status Key:** 🟢 Active | 🟡 Idle/Inactive (Connected) | ⚪ Off / Breaker Open | 🔴 Error/Unknown
        """)
    # --- End of Device Status Overview ---

    st.divider()

    # --- Steam Presence ---
    with st.container(border=True):  # Optional container
        st.subheader("Steam Presence")
        cols_steam = st.columns(2)
        with cols_steam[0]:
            utils.display_metric("Steam Present?", "CORE_STEAM_PRESENT")
        with cols_steam[1]:
            utils.display_metric("High Steam Present?", "CORE_HIGH_STEAM_PRESENT")

    st.divider()

    # --- Turbine Details ---
    st.subheader("Turbine Details")  # Group turbines under one subheader
    turbine_active_count = 0
    for i in range(3):
        # Check if data is valid before displaying by checking a key variable like RPM
        rpm_value = utils.fetch_variable_value(f"STEAM_TURBINE_{i}_RPM")
        if not (isinstance(rpm_value, str) and "Error:" in rpm_value):
            display_turbine_status(i)  # Now displays gauges
            turbine_active_count += 1
            st.markdown("<br>", unsafe_allow_html=True)  # Add space between turbine details

    if turbine_active_count == 0:
        st.caption("No active turbines detected or data unavailable.")

    st.divider()

    # --- Generator Details ---
    st.subheader("Generator Details")  # Group generators under one subheader
    generator_active_count = 0
    for i in range(3):
        # Check if data is valid before displaying
        kw_value = utils.fetch_variable_value(f"GENERATOR_{i}_KW")
        if not (isinstance(kw_value, str) and "Error:" in kw_value):
            display_generator_status(i)  # Now displays gauges/icons
            generator_active_count += 1
            st.markdown("<br>", unsafe_allow_html=True)  # Add space between generator details

    if generator_active_count == 0:
        st.caption("No active generators detected or data unavailable.")

    # Total Power display moved to top
