import streamlit as st
import requests
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="CommCare Analytics", layout="wide")
st.title("📊 Enumerator Performance Dashboard")

# 2. Fetching and Processing Function
@st.cache_data(ttl=600)  # Caches for 10 minutes to save API hits
def get_commcare_data():
    # Use secrets for security
    domain = st.secrets["commcare"]["domain"]
    username = st.secrets["commcare"]["username"]
    api_key = st.secrets["commcare"]["api_key"]
    
    # Form API endpoint
    url = f"https://www.commcarehq.org/a/{domain}/api/v0.5/form/"
    
    try:
        response = requests.get(url, auth=(username, api_key))
        response.raise_for_status()
        data = response.json()
        
        # Flatten the nested JSON structure
        # CommCare forms are deeply nested, json_normalize fixes this
        df = pd.json_normalize(data.get("objects", []))
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

# 3. Main Dashboard
df = get_commcare_data()

if not df.empty:
    # Rename columns to be more readable if they exist
    # CommCare usually stores the user in 'metadata.username' or 'form.meta.username'
    # We look for the most common path
    user_col = "metadata.username" if "metadata.username" in df.columns else "form.meta.username"
    
    if user_col in df.columns:
        # --- Analysis ---
        st.subheader("Submissions per Enumerator")
        
        # Count submissions per user
        stats = df[user_col].value_counts().reset_index()
        stats.columns = ['Enumerator', 'Total Submissions']
        
        # Display Bar Chart
        st.bar_chart(stats.set_index('Enumerator'))
        
        # Display Table
        st.table(stats)
        
        # --- Raw Data Preview ---
        with st.expander("View Raw Data"):
            st.dataframe(df)
    else:
        st.warning(f"Could not identify the username column. Available columns: {df.columns.tolist()}")
else:
    st.info("No data found or connection failed. Check your API credentials.")

# 4. Sidebar Refresh
if st.sidebar.button("Refresh Data"):
    st.cache_data.clear()
    st.rerun()
