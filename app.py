import streamlit as st
import requests
import pandas as pd

# 1. Page Config
st.set_page_config(page_title="CommCare Analytics", layout="wide")
st.title("📊 Enumerator Performance Dashboard")

# 2. Fetching Function
@st.cache_data(ttl=600)
def get_commcare_data():
    try:
        # Access secrets directly
        domain = st.secrets["commcare"]["domain"]
        username = st.secrets["commcare"]["username"]
        api_key = st.secrets["commcare"]["api_key"]
    except KeyError as e:
        st.error(f"Missing Secret: {e}. Please ensure secrets.toml is configured.")
        return None

    # Construct URL
    url = f"https://www.commcarehq.org/a/{domain}/api/v0.5/form/"
    
    # Debug: Check if credentials look sane (not empty)
    if not username or not api_key or not domain:
        st.error("Credentials found but seem to be empty strings.")
        return None

    try:
        # Perform Request
        response = requests.get(url, auth=(username, api_key))
        
        # If unauthorized, show details
        if response.status_code == 401:
            st.error("401 Unauthorized: The server rejected your credentials. "
                     "Double-check your API key and email in the Streamlit Cloud 'Secrets' tab.")
            return None
            
        response.raise_for_status()
        
        data = response.json()
        return pd.json_normalize(data.get("objects", []))
        
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return None

# 3. Main Logic
df = get_commcare_data()

if df is not None and not df.empty:
    # Attempt to find the username column
    # Check both potential CommCare API paths
    target_col = None
    for col in ["metadata.username", "form.meta.username"]:
        if col in df.columns:
            target_col = col
            break
    
    if target_col:
        st.subheader("Submissions per Enumerator")
        stats = df[target_col].value_counts().reset_index()
        stats.columns = ['Enumerator', 'Total Submissions']
        
        st.bar_chart(stats.set_index('Enumerator'))
        st.table(stats)
    else:
        st.warning("Data loaded, but could not identify the 'username' column.")
        st.write("Available columns:", df.columns.tolist())
elif df is not None:
    st.info("No forms found in this domain.")
