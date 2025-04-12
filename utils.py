# utils.py
import math  # Import math for isnan check

import plotly.graph_objects as go
import requests
import streamlit as st

import config  # Import configuration


# Cache data fetching
@st.cache_data(ttl=config.DEFAULT_REFRESH_RATE_SECONDS * 0.9)
def fetch_variable_value(variable_name):
    """Fetches a single variable's value from the webserver."""
    if not isinstance(variable_name, str):
        return f"Error: Invalid variable name type ({type(variable_name)})"

    params = {"Variable": variable_name}
    value = f"Error: Var '{variable_name}' not found"
    try:
        response = requests.get(config.WEBSERVER_URL, params=params, timeout=1)
        response.raise_for_status()
        value = response.text.strip()
        if value:
            try:
                value = float(value)
                if math.isnan(value): value = "Error: Received NaN"
            except ValueError:
                if value.upper() == 'TRUE':
                    value = True
                elif value.upper() == 'FALSE':
                    value = False
        else:
            value = "Error: Empty value received"

    except requests.exceptions.ConnectionError:
        value = "Error: Connection refused."
    except requests.exceptions.Timeout:
        value = "Error: Timeout."
    except requests.exceptions.RequestException as e:
        value = f"Error: {e}"
    return value


# Generic metric display - UPDATED WITH DELTA LOGIC & FONT SIZE ADJUSTMENT
def display_metric(label, variable_name, help_text=None, delta_color="normal"):
    """
    Fetches and displays a single metric, including a delta from the previous value.
    Uses st.session_state to store the previous value.
    Includes CSS to adjust the metric label and value font sizes.
    """
    # --- CSS Injection for Metric Label & Value Font Sizes ---
    # Apply custom CSS to adjust font sizes within the metric component.
    # This CSS is applied once per metric display call.
    st.markdown("""
        <style>
            /* Target the label within the metric component */
            div[data-testid="stMetric"] label[data-testid="stMetricLabel"] {
                font-size: 1.1rem; /* Adjust size as needed, e.g., '1rem', '110%' */
                /* font-weight: bold; */ /* Optional: make label bold */
            }

            /* Target the value within the metric component */
            div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
                font-size: 1.75rem; /* Adjust size as needed, default is often larger */
            }
        </style>
        """, unsafe_allow_html=True)
    # --- End CSS Injection ---

    current_value = fetch_variable_value(variable_name)
    prev_value_key = f"previous_{variable_name}"
    previous_value = st.session_state.get(prev_value_key, None)
    delta_value_display = None  # For passing to st.metric

    # Calculate delta only if current and previous values are numeric
    is_current_numeric = isinstance(current_value, (int, float))
    is_previous_numeric = isinstance(previous_value, (int, float))

    if is_current_numeric and is_previous_numeric:
        delta_raw = current_value - previous_value
        # Only display delta if it's not zero (or handle as needed)
        if delta_raw != 0:
            delta_value_display = delta_raw  # Pass raw delta to st.metric

    # Display the metric
    if isinstance(current_value, str) and "Error:" in current_value:
        st.metric(label=label, value="N/A", delta=current_value, delta_color="off", help=help_text)
        # Do not update session state if current value is an error
    else:
        display_val_str = ""
        if isinstance(current_value, float):
            display_val_str = f"{current_value:.2f}"
        elif isinstance(current_value, bool):
            display_val_str = "TRUE" if current_value else "FALSE"
            delta_value_display = None  # No delta for boolean changes
        else:
            display_val_str = str(current_value)  # Handle ints or other types

        # Display the metric using Streamlit's built-in component
        st.metric(label=label, value=display_val_str, delta=delta_value_display, delta_color=delta_color,
                  help=help_text)

        # Update session state with the current value for the next run, only if it's valid
        if is_current_numeric or isinstance(current_value, bool):
            st.session_state[prev_value_key] = current_value


# Gauge display (Handles direct values or variable names for ranges) - UPDATED for neutral display
def display_gauge(title, value_var, range_min_input, range_max_input, op_min_input=None, op_max_input=None, unit=""):
    """
    Fetches data and displays a Plotly gauge chart with clearer colors and adjusted fonts.
    Shows a neutral state if essential data (value, min, max) is invalid/unavailable.
    Range inputs can be variable names (str) or direct numerical values.
    Includes specific logic for Frequency gauge colors.
    """
    # Fetch all potentially needed values
    value = fetch_variable_value(value_var)
    range_min = fetch_variable_value(range_min_input) if isinstance(range_min_input, str) else range_min_input
    range_max = fetch_variable_value(range_max_input) if isinstance(range_max_input, str) else range_max_input
    op_min = fetch_variable_value(op_min_input) if isinstance(op_min_input, str) else op_min_input
    op_max = fetch_variable_value(op_max_input) if isinstance(op_max_input, str) else op_max_input

    # --- Check data validity ---
    value_valid = isinstance(value, (int, float))
    range_min_valid = isinstance(range_min, (int, float))
    range_max_valid = isinstance(range_max, (int, float))
    op_min_valid = isinstance(op_min, (int, float))
    op_max_valid = isinstance(op_max, (int, float))

    is_range_sensible = not (range_min_valid and range_max_valid) or (range_max > range_min)
    is_data_valid = value_valid and range_min_valid and range_max_valid and is_range_sensible
    display_value = value if is_data_valid else None
    number_text = "N/A" if not is_data_valid else None  # Used to hide number display if N/A
    gauge_range = [range_min, range_max] if is_data_valid else [0, 1]
    gauge_title = f"{title} ({unit})" if unit and is_data_valid else title  # Add unit only if valid
    steps = []
    threshold_val = gauge_range[1]  # Default threshold

    # Define colors (moved up for clarity)
    color_cold = "cornflowerblue";
    color_operative = "mediumseagreen";
    color_hot = "indianred"
    color_high_pressure = "indianred";
    color_normal_pressure = "mediumseagreen"
    color_good = "mediumseagreen";
    color_bad = "indianred"
    color_warning = "gold";
    color_off = "lightsteelblue";
    color_neutral = "lightgrey"

    if is_data_valid:
        # --- Determine Gauge Steps and Threshold based on Title/Data ---
        op_range_valid = not (op_min_valid and op_max_valid) or (op_max > op_min)

        if "Frequency" in title:
            # Specific logic for Frequency gauge colors
            freq_target_min = op_min if op_min_valid else 49.5
            freq_target_max = op_max if op_max_valid else 50.5
            freq_warn_low = freq_target_min - 1.5;
            freq_warn_high = freq_target_max + 1.5
            freq_off_threshold = 0.5
            threshold_val = freq_target_min  # Red line at start of good zone
            if abs(value) < freq_off_threshold:
                steps = [{'range': gauge_range, 'color': color_off}];
                gauge_title = f"{title} (Off)"
            else:
                steps = [
                    {'range': [gauge_range[0], freq_warn_low], 'color': color_bad},
                    {'range': [freq_warn_low, freq_target_min], 'color': color_warning},
                    {'range': [freq_target_min, freq_target_max], 'color': color_good},
                    {'range': [freq_target_max, freq_warn_high], 'color': color_warning},
                    {'range': [freq_warn_high, gauge_range[1]], 'color': color_bad}]
                # Filter out steps where start >= end (can happen with extreme ranges)
                steps = [s for s in steps if s['range'][0] < s['range'][1]]

        elif "Temperature" in title:
            # Logic for Temperature (Cold/Operative/Hot)
            if op_min_valid and op_max_valid and op_range_valid and op_max <= range_max and op_min >= range_min:
                steps = [
                    {'range': [range_min, op_min], 'color': color_cold},
                    {'range': [op_min, op_max], 'color': color_operative},
                    {'range': [op_max, range_max], 'color': color_hot}
                ]
                threshold_val = op_max  # Red line at start of hot zone
            elif op_max_valid and op_max >= range_min and op_max <= range_max:  # Only upper threshold provided
                steps = [
                    {'range': [range_min, op_max], 'color': color_operative},  # Assume below op_max is operative
                    {'range': [op_max, range_max], 'color': color_hot}
                ]
                threshold_val = op_max
            else:  # No valid operative range defined
                steps = [{'range': gauge_range, 'color': color_neutral}]
                threshold_val = range_max  # No meaningful threshold

        elif "Pressure" in title:
            # Logic for Pressure (Normal/High)
            if op_max_valid and op_max >= range_min and op_max <= range_max:
                steps = [
                    {'range': [range_min, op_max], 'color': color_normal_pressure},
                    {'range': [op_max, range_max], 'color': color_high_pressure}
                ]
                threshold_val = op_max  # Red line at start of high pressure
            else:  # No valid operative range defined
                steps = [{'range': gauge_range, 'color': color_neutral}]
                threshold_val = range_max

        else:  # Default logic for other gauges (e.g., Integrity, Wear, Level)
            if op_min_valid and op_max_valid and op_range_valid and op_max <= range_max and op_min >= range_min:
                # Three zones defined (e.g., Bad/Good/Bad)
                steps = [
                    {'range': [range_min, op_min], 'color': color_bad},
                    {'range': [op_min, op_max], 'color': color_good},
                    {'range': [op_max, range_max], 'color': color_bad}
                ]
                threshold_val = op_min  # Red line typically at start of first 'bad' or end of 'good'
            elif op_max_valid and op_max >= range_min and op_max <= range_max:
                # Two zones defined by a single threshold (op_max)
                threshold_val = op_max
                # Determine if higher is better (Integrity) or worse (Wear, Level Low Fuel)
                if "Integrity" in title:  # Higher is better
                    steps = [
                        {'range': [range_min, threshold_val], 'color': color_bad},
                        {'range': [threshold_val, range_max], 'color': color_good}
                    ]
                else:  # Higher is worse (Wear) or below threshold is bad (Level)
                    steps = [
                        {'range': [range_min, threshold_val], 'color': color_good},
                        {'range': [threshold_val, range_max], 'color': color_bad}
                    ]
            else:  # No valid operative range defined
                steps = [{'range': gauge_range, 'color': color_neutral}]
                threshold_val = range_min + (range_max - range_min) / 2  # Default threshold halfway

    else:  # Data is invalid
        gauge_title = f"{title} (N/A)"
        steps = [{'range': gauge_range, 'color': color_neutral}]
        threshold_val = gauge_range[1]  # Default threshold to max

    # --- Create Plotly Gauge Figure ---
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=display_value,  # Will be None if data is invalid, hiding the needle
        number={
            # --- FONT SIZE ADJUSTMENT HERE ---
            'font': {'size': 28},  # Reduced size from 36
            # --- END FONT SIZE ADJUSTMENT ---
            'valueformat': '.1f',  # Apply formatting, will be overridden by text below if N/A
            'suffix': unit if is_data_valid and unit else ""  # Show unit only if valid
        },
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': gauge_title, 'font': {'size': 16}},  # Use the determined title
        gauge={
            'axis': {'range': list(gauge_range), 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "rgba(0,0,0,0)"},  # Invisible bar to allow steps to show
            'bgcolor': "white",
            'borderwidth': 1,
            'bordercolor': "gray",
            'steps': steps,  # Use the determined steps
            'threshold': {
                'line': {'color': "red" if is_data_valid else "grey", 'width': 3},
                'thickness': 0.9,
                'value': threshold_val  # Use the determined threshold
            }
        }
    ))

    # If data is invalid, add "N/A" text annotation instead of trying to display a number
    if not is_data_valid:
        fig.add_annotation(
            x=0.5, y=0.3,  # Position the text centrally below the title
            text="N/A",
            showarrow=False,
            # Match the adjusted number font size for consistency when showing "N/A"
            font=dict(size=28, color="grey"),  # Changed size from 36 to 28
            align="center"
        )
        # Ensure the number part of the indicator is hidden when N/A
        fig.update_traces(number={'valueformat': ''})  # Clear format to hide automatic number

    # Update layout for consistent appearance
    fig.update_layout(
        height=190,  # Fixed height
        margin=dict(l=20, r=20, t=50, b=10),  # Adjust margins
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
        font={'color': "grey", 'family': "Arial"}  # Default font settings
    )

    # Display the chart
    chart_key = f"gauge_{value_var}"  # Unique key for the chart element
    st.plotly_chart(fig, use_container_width=True, key=chart_key)


# Generic progress display
def display_progress(label, variable_name, max_value=100, help_text=None):
    """Fetches and displays a progress bar."""
    value = fetch_variable_value(variable_name)
    if isinstance(value, (int, float)):
        # Ensure value is within 0 to max_value before calculating percentage
        clamped_value = max(0.0, min(float(value), float(max_value)))
        progress_percentage = clamped_value / float(max_value)
        # Format text based on whether it's a percentage or absolute value
        progress_text = f"{clamped_value:.1f}%" if max_value == 100 else f"{clamped_value:.1f} / {max_value}"
        # Display label separately for better control
        st.text(label)
        st.progress(progress_percentage, text=progress_text)
    else:
        st.text(f"{label}: N/A ({value})")
        st.progress(0.0, text="N/A")  # Show an empty progress bar


# Helper for Boolean Status
def display_boolean_status(label, variable_name):
    """Fetches a boolean variable and displays status with a larger icon."""
    value = fetch_variable_value(variable_name)
    icon = "❓"  # Default icon: Unknown
    status_text = f"<small>Invalid ({value})</small>"  # Default text for non-boolean/non-error

    if isinstance(value, bool):
        icon = "✅" if value else "❌"  # Green check for True, Red X for False
        status_text = ""  # No extra text needed for clear boolean
    elif isinstance(value, str) and "Error:" in value:
        icon = "⚠️"  # Warning icon for errors
        status_text = f"<small>N/A ({value})</small>"  # Show error message small

    # Use markdown to display label, icon, and status text
    st.markdown(f"""
    <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
        <span style="font-weight: bold; margin-right: 8px;">{label}:</span>
        <span style="font-size: 1.2em; margin-right: 4px;">{icon}</span>
        {status_text}
    </div>
    """, unsafe_allow_html=True)
