# tabs/power_gen.py
import streamlit as st

import utils  # Import helpers from utils.py


# No need to import config here unless specific constants are needed directly

# --- Specific Helper Functions for this Tab ---

def display_turbine_status(turbine_index):
    """Displays status metrics for a single steam turbine."""
    # Use utils functions for fetching and displaying
    st.subheader(f"Steam Turbine {turbine_index}")
    cols = st.columns(3)
    with cols[0]:
        utils.display_metric(f"Turbine {turbine_index} RPM", f"STEAM_TURBINE_{turbine_index}_RPM")
    with cols[1]:
        utils.display_metric(f"Turbine {turbine_index} Temp (°C)", f"STEAM_TURBINE_{turbine_index}_TEMPERATURE")
    with cols[2]:
        utils.display_metric(f"Turbine {turbine_index} Pressure", f"STEAM_TURBINE_{turbine_index}_PRESSURE")


def display_generator_status(gen_index):
    """Displays status metrics for a single generator."""
    # Use utils functions for fetching and displaying
    st.subheader(f"Generator {gen_index}")
    cols = st.columns(3)
    with cols[0]:
        utils.display_metric(f"Gen {gen_index} Output (kW)", f"GENERATOR_{gen_index}_KW")
        utils.display_metric(f"Gen {gen_index} Voltage (V)", f"GENERATOR_{gen_index}_V")
    with cols[1]:
        utils.display_metric(f"Gen {gen_index} Current (A)", f"GENERATOR_{gen_index}_A")
        utils.display_metric(f"Gen {gen_index} Frequency (Hz)", f"GENERATOR_{gen_index}_HERTZ")
    with cols[2]:
        # Use the generic display_metric which handles boolean conversion now
        utils.display_metric(f"Gen {gen_index} Breaker", f"GENERATOR_{gen_index}_BREAKER",
                             help_text="TRUE: Open, FALSE: Close")


# --- Main Display Function for the Tab ---

def display_tab():
    """Displays the content for the Steam & Power Generation tab."""
    st.header("Steam & Power Generation")

    # Steam Presence - uses generic helper
    cols_steam = st.columns(2)
    with cols_steam[0]:
        utils.display_metric("Steam Present?", "CORE_STEAM_PRESENT")
    with cols_steam[1]:
        utils.display_metric("High Steam Present?", "CORE_HIGH_STEAM_PRESENT")

    st.divider()

    # Turbines - uses local helper
    # Assuming max 3 turbines based on variable names
    for i in range(3):
        # Basic check if turbine exists (e.g., if RPM is available and not an error)
        rpm_value = utils.fetch_variable_value(f"STEAM_TURBINE_{i}_RPM")
        # Check if it's not an error string before proceeding
        if not (isinstance(rpm_value, str) and "Error:" in rpm_value):
            display_turbine_status(i)  # Call local helper
            st.divider()

    # Generators - uses local helper
    total_kw = 0.0
    for i in range(3):
        # Basic check if generator exists (e.g., if KW is available and not an error)
        kw_value = utils.fetch_variable_value(f"GENERATOR_{i}_KW")
        if not (isinstance(kw_value, str) and "Error:" in kw_value):
            display_generator_status(i)  # Call local helper
            st.divider()
            if isinstance(kw_value, float):
                total_kw += kw_value

    # Display Total Power
    st.header(f"Total Generator Output: {total_kw:.2f} kW")
