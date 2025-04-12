# utils.py
import plotly.graph_objects as go
import requests
import streamlit as st

import config  # Import configuration


# Cache data fetching
@st.cache_data(ttl=config.DEFAULT_REFRESH_RATE_SECONDS * 0.9)
def fetch_variable_value(variable_name):
    """Fetches a single variable's value from the webserver."""
    # Ensure variable_name is a string before making the request
    if not isinstance(variable_name, str):
        return f"Error: Invalid variable name type ({type(variable_name)})"

    params = {"Variable": variable_name}
    value = f"Error: Var '{variable_name}' not found"  # Default if not fetched
    try:
        # Use URL from config
        response = requests.get(config.WEBSERVER_URL, params=params, timeout=1)
        response.raise_for_status()
        value = response.text.strip()
        # Attempt conversion only if not empty or whitespace
        if value:
            try:
                value = float(value)
            except ValueError:
                if value.upper() == 'TRUE':
                    value = True
                elif value.upper() == 'FALSE':
                    value = False
                # Keep as string if it's not convertible and not TRUE/FALSE
        else:
            value = "Error: Empty value received"  # Treat empty string as an error

    except requests.exceptions.ConnectionError:
        value = "Error: Connection refused."
    except requests.exceptions.Timeout:
        value = "Error: Timeout."
    except requests.exceptions.RequestException as e:
        value = f"Error: {e}"  # Catch other potential request errors
    return value

# Generic metric display
def display_metric(label, variable_name, help_text=None):
    """Fetches and displays a single metric."""
    value = fetch_variable_value(variable_name)
    if isinstance(value, str) and "Error:" in value:
        st.metric(label=label, value="N/A", delta=value, delta_color="off", help=help_text)
    else:
        if isinstance(value, float):
            st.metric(label=label, value=f"{value:.2f}", help=help_text)
        elif isinstance(value, bool):
            st.metric(label=label, value="TRUE" if value else "FALSE", help=help_text)
        else:
            st.metric(label=label, value=value, help=help_text)


# Gauge display (Handles direct values or variable names for ranges) - UPDATED for neutral display
def display_gauge(title, value_var, range_min_input, range_max_input, op_min_input=None, op_max_input=None, unit=""):
    """
    Fetches data and displays a Plotly gauge chart with clearer colors and adjusted fonts.
    Shows a neutral state if essential data (value, min, max) is invalid/unavailable.
    Range inputs can be variable names (str) or direct numerical values.
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

    # Ensure range_max is strictly greater than range_min if both are valid
    is_range_sensible = not (range_min_valid and range_max_valid) or (range_max > range_min)

    is_data_valid = value_valid and range_min_valid and range_max_valid and is_range_sensible
    display_value = value if is_data_valid else None  # Use None for gauge value if data invalid
    number_text = "N/A" if not is_data_valid else None  # Display N/A text if data invalid
    gauge_range = [range_min, range_max] if is_data_valid else [0, 1]  # Default range if invalid
    gauge_title = f"{title} ({unit})" if unit else title
    steps = []
    # Ensure threshold_val is defined even if data is invalid
    threshold_val = gauge_range[1]  # Default threshold to max of current range
    bar_color = "darkblue"  # Default value bar color (though it's transparent now)

    if is_data_valid:
        # --- Calculate steps and threshold ONLY if data is valid ---
        color_cold = "cornflowerblue"
        color_operative = "mediumseagreen"
        color_hot = "indianred"
        color_high_pressure = "indianred"
        color_normal_pressure = "mediumseagreen"
        color_good = "mediumseagreen"
        color_bad = "indianred"

        # Ensure op_min < op_max if both are valid
        op_range_valid = not (op_min_valid and op_max_valid) or (op_max > op_min)

        if "Temperature" in title:
            # Use op_min as start of green, op_max as start of red
            if op_min_valid and op_max_valid and op_range_valid and op_max <= range_max and op_min >= range_min:
                steps = [
                    {'range': [range_min, op_min], 'color': color_cold},
                    {'range': [op_min, op_max], 'color': color_operative},
                    {'range': [op_max, range_max], 'color': color_hot}]
                threshold_val = op_max  # Threshold marks start of "hot" zone
            else:  # Fallback if operative range isn't fully defined/valid for temp
                steps = [{'range': [range_min, range_max], 'color': "lightgray"}]
                threshold_val = range_max
        elif "Pressure" in title:
            # Use op_max as start of red zone
            if op_max_valid and op_max >= range_min and op_max <= range_max:
                steps = [
                    {'range': [range_min, op_max], 'color': color_normal_pressure},
                    {'range': [op_max, range_max], 'color': color_high_pressure}]
                threshold_val = op_max  # Threshold marks start of "high pressure" zone
            else:  # Fallback for pressure
                steps = [{'range': [range_min, range_max], 'color': "lightgray"}]
                threshold_val = range_max
        else:  # Default logic for other gauges (Integrity, Wear, Rod Temp)
            # Use op_max as the threshold between good/bad if provided
            if op_max_valid and op_max >= range_min and op_max <= range_max:
                threshold_val = op_max
            else:  # Otherwise default to midpoint
                threshold_val = range_min + (range_max - range_min) / 2

            if "Integrity" in title:  # Higher is better
                steps = [
                    {'range': [range_min, threshold_val], 'color': color_bad},
                    {'range': [threshold_val, range_max], 'color': color_good}]
            else:  # Assume higher is worse (Wear, Rod Temp)
                steps = [
                    {'range': [range_min, threshold_val], 'color': color_good},
                    {'range': [threshold_val, range_max], 'color': color_bad}]
            # threshold_val is already set
    else:
        # --- Use neutral settings if data is invalid ---
        gauge_title = f"{title} (N/A)"
        steps = [{'range': gauge_range, 'color': 'lightgrey'}]  # Single grey step
        threshold_val = gauge_range[1]  # Threshold at max of default range
        bar_color = "grey"  # Grey bar if value is shown

    # --- Create the Gauge Figure ---
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=display_value,  # Use None if data invalid
        number={
            'font': {'size': 36},
            'valueformat': '.1f' if number_text is None else '',  # Apply format only if showing number
            'suffix': unit if number_text is None else '',
        },
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': gauge_title, 'font': {'size': 16}},
        gauge={
            'axis': {'range': list(gauge_range), 'tickwidth': 1, 'tickcolor': "darkblue"},  # Ensure range is list
            'bar': {'color': "rgba(0,0,0,0)"},  # Keep value bar transparent
            'bgcolor': "white",
            'borderwidth': 1,
            'bordercolor': "gray",
            'steps': steps,
            'threshold': {
                'line': {'color': "red" if is_data_valid else "grey", 'width': 3},  # Grey threshold if invalid
                'thickness': 0.9,
                'value': threshold_val  # Use the determined threshold value
            }
        }
    ))

    # Add N/A text annotation if data is invalid
    if not is_data_valid:
        fig.add_annotation(
            x=0.5, y=0.3,  # Adjust position as needed
            text="N/A",
            showarrow=False,
            font=dict(size=36, color="grey"),
            align="center"
        )

    fig.update_layout(
        height=210,
        margin=dict(l=20, r=20, t=50, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': "grey", 'family': "Arial"}
    )
    st.plotly_chart(fig, use_container_width=True)

# Generic progress display
def display_progress(label, variable_name, max_value=100, help_text=None):
    """Fetches and displays a progress bar."""
    value = fetch_variable_value(variable_name)
    if isinstance(value, (int, float)):
        progress_value = max(0.0, min(float(value), float(max_value))) / float(max_value)
        st.text(label)
        st.progress(progress_value, text=f"{value:.1f}%" if max_value == 100 else f"{value:.1f}")
    else:
        st.text(f"{label}: N/A ({value})")


# Helper for Boolean Status
def display_boolean_status(label, variable_name):
    """Fetches a boolean variable and displays status with a larger icon."""
    value = fetch_variable_value(variable_name)
    if isinstance(value, bool):
        icon = "✅" if value else "❌"
        st.markdown(f"""
        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
            <span style="font-weight: bold; margin-right: 8px;">{label}:</span>
            <span style="font-size: 1.2em;">{icon}</span>
        </div>
        """, unsafe_allow_html=True)
    elif isinstance(value, str) and "Error:" in value:
        st.markdown(f"""
         <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
             <span style="font-weight: bold; margin-right: 8px;">{label}:</span>
             <small>N/A ({value})</small>
         </div>
         """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
         <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
             <span style="font-weight: bold; margin-right: 8px;">{label}:</span>
             <small>Invalid ({value})</small>
         </div>
         """, unsafe_allow_html=True)
