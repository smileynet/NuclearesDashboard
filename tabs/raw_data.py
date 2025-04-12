# tabs/raw_data.py
import streamlit as st

import config  # Import config to get the VARIABLES list
import utils  # Import helpers from utils.py


# --- Main Display Function for the Tab ---

def display_tab():
    """Displays the content for the Raw Data Viewer tab."""
    st.header("Raw Variable Viewer")
    st.info("Select variables below to view their current raw values.")

    # Variable Selection using multiselect
    selected_variables_raw = st.multiselect(
        "Select variables to view:",
        options=config.VARIABLES,  # Use variables list from config
        default=["CORE_TEMP", "CORE_PRESSURE", "TIME_STAMP"],  # Sensible defaults
        key="raw_data_multiselect"  # Keep the unique key
    )

    # Display selected variables
    if not selected_variables_raw:
        st.warning("Select variables above to view their raw values.")
    else:
        num_columns_raw = 3
        cols_raw = st.columns(num_columns_raw)
        # Display selected raw variables using the generic metric display
        for i, variable in enumerate(selected_variables_raw):
            col_index = i % num_columns_raw
            with cols_raw[col_index]:
                utils.display_metric(variable, variable)  # Label is same as variable name
