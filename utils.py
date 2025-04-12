# utils.py
import plotly.graph_objects as go
import requests
import streamlit as st

import config  # Import configuration


# Cache data fetching
@st.cache_data(ttl=config.DEFAULT_REFRESH_RATE_SECONDS * 0.9)
def fetch_variable_value(variable_name):
    # ... (keep the full fetch_variable_value function here) ...
    if not isinstance(variable_name, str):
        return f"Error: Invalid variable name type ({type(variable_name)})"
    params = {"Variable": variable_name}
    value = f"Error: Var '{variable_name}' not found"
    try:
        response = requests.get(config.WEBSERVER_URL, params=params, timeout=1)
        response.raise_for_status()
        value = response.text.strip()
        try:
            value = float(value)
        except ValueError:
            if value.upper() == 'TRUE':
                value = True
            elif value.upper() == 'FALSE':
                value = False
    except requests.exceptions.ConnectionError:
        value = "Error: Connection refused."
    except requests.exceptions.Timeout:
        value = "Error: Timeout."
    except requests.exceptions.RequestException as e:
        value = f"Error: {e}"
    return value


# Generic metric display
def display_metric(label, variable_name, help_text=None):
    # ... (keep the full display_metric function here) ...
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


# Generic gauge display
def display_gauge(title, value_var, range_min_input, range_max_input, op_min_input=None, op_max_input=None, unit=""):
    # ... (keep the full display_gauge function here) ...
    value = fetch_variable_value(value_var)
    if isinstance(range_min_input, str):
        range_min = fetch_variable_value(range_min_input)
    elif isinstance(range_min_input, (int, float)):
        range_min = range_min_input
    else:
        range_min = f"Error: Invalid type for range_min ({type(range_min_input)})"

    if isinstance(range_max_input, str):
        range_max = fetch_variable_value(range_max_input)
    elif isinstance(range_max_input, (int, float)):
        range_max = range_max_input
    else:
        range_max = f"Error: Invalid type for range_max ({type(range_max_input)})"

    if isinstance(op_min_input, str):
        op_min = fetch_variable_value(op_min_input)
    elif isinstance(op_min_input, (int, float)):
        op_min = op_min_input
    else:
        op_min = None

    if isinstance(op_max_input, str):
        op_max = fetch_variable_value(op_max_input)
    elif isinstance(op_max_input, (int, float)):
        op_max = op_max_input
    else:
        op_max = None

    essential_values = [value, range_min, range_max]
    if not all(isinstance(v, (int, float)) for v in essential_values):
        st.warning(f"Cannot display gauge for '{title}': Invalid data received.")
        st.caption(f"Value: {value}, Min: {range_min}, Max: {range_max}, OpMin: {op_min}, OpMax: {op_max}")
        return

    if range_min >= range_max:
        st.warning(f"Cannot display gauge for '{title}': Min range ({range_min}) >= Max range ({range_max}).")
        return

    steps = []
    op_min_valid = isinstance(op_min, (int, float))
    op_max_valid = isinstance(op_max, (int, float))

    if op_min_valid and op_max_valid:
        steps = [{'range': [range_min, op_min], 'color': "lightblue"},
                 {'range': [op_min, op_max], 'color': "lightgreen"},
                 {'range': [op_max, range_max], 'color': "lightcoral"}]
        threshold_value = op_max
    elif op_max_valid:
        steps = [{'range': [range_min, op_max], 'color': "lightgreen"},
                 {'range': [op_max, range_max], 'color': "lightcoral"}]
        threshold_value = op_max
    else:
        steps = [{'range': [range_min, range_max], 'color': "lightgray"}]
        threshold_value = range_max

    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=value, domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"{title} ({unit})" if unit else title, 'font': {'size': 18}},
        gauge={'axis': {'range': [range_min, range_max], 'tickwidth': 1, 'tickcolor': "darkblue"},
               'bar': {'color': "darkblue"}, 'bgcolor': "white", 'borderwidth': 2, 'bordercolor': "gray",
               'steps': steps,
               'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': threshold_value}}))
    fig.update_layout(height=200, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor='rgba(0,0,0,0)',
                      font={'color': "gray", 'family': "Arial"})
    st.plotly_chart(fig, use_container_width=True)


# Generic progress display
def display_progress(label, variable_name, max_value=100, help_text=None):
    # ... (keep the full display_progress function here) ...
    value = fetch_variable_value(variable_name)
    if isinstance(value, (int, float)):
        progress_value = max(0.0, min(float(value), float(max_value))) / float(max_value)
        st.text(label)
        st.progress(progress_value, text=f"{value:.1f}%" if max_value == 100 else f"{value:.1f}")
    else:
        st.text(f"{label}: N/A ({value})")
