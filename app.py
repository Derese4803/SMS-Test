import streamlit as st
import requests
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="CommCare Data Viewer", layout="wide")
st.title("📊 CommCare Data Explorer")

# 2. Fetching Function with Caching
@st.cache_data(ttl=3600) # Caches the data for 1 hour
def fetch_commcare_data(endpoint):
    username = st.secrets["commcare"]["username"]
    api_key = st.secrets["commcare"]["api_key"]
    domain = st.secrets["commcare"]["domain"]
    
    url = f"https://www.commcarehq.org/a/{domain}/api/v0.5/{endpoint}/"
    
    try:
        response = requests.get(url, auth=(username, api_key))
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error connecting to CommCare: {e}")
        return None

# 3. Main Logic
if st.button("Load Case Data"):
    with st.spinner("Fetching data from CommCare..."):
        data = fetch_commcare_data("case")
        
        if data and "objects" in data:
            # Convert JSON response to a Pandas DataFrame
            df = pd.DataFrame(data["objects"])
            st.success("Data successfully retrieved!")
            st.dataframe(df) # Displays an interactive table
        else:
            st.warning("No data found or request failed.")

# Sidebar for extra info
st.sidebar.header("About")
st.sidebar.info("This app connects to the CommCare domain: " + st.secrets["commcare"]["domain"])
