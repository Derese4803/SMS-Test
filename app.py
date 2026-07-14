import streamlit as st
import requests
import pandas as pd

# 1. Page Config
st.set_page_config(page_title="CommCare Data Viewer", layout="wide")
st.title("☕ CommCare Coffee-23 Dashboard")

# 2. Fetching Function
@st.cache_data(ttl=3600)
def fetch_cases():
    # Retrieve credentials from your secrets.toml
    username = st.secrets["commcare"]["username"]
    api_key = st.secrets["commcare"]["api_key"]
    domain = st.secrets["commcare"]["domain"]
    
    # API URL for Cases
    url = f"https://www.commcarehq.org/a/{domain}/api/v0.5/case/"
    
    try:
        # Authentication
        response = requests.get(url, auth=(username, api_key))
        response.raise_for_status()
        
        # Parse JSON
        data = response.json()
        
        # Use json_normalize to flatten nested JSON structures
        if "objects" in data:
            df = pd.json_normalize(data["objects"])
            return df
        return None
        
    except Exception as e:
        st.error(f"Error: {e}")
        return None

# 3. Main Interface
if st.button("🚀 Fetch Data from CommCare"):
    with st.spinner("Downloading your data..."):
        df = fetch_cases()
        
        if df is not None and not df.empty:
            st.success("Data loaded!")
            st.dataframe(df)
            
            # Optional: Add a download button
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Download as CSV", csv, "commcare_data.csv", "text/csv")
        else:
            st.warning("No cases found or connection error.")
