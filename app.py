import streamlit as st
import requests
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="CommCare Analytics", layout="wide")
st.title("📊 Enumerator Performance Dashboard")

# 2. Fetching and Processing Function
@st.cache_data(ttl=600)
def get_commcare_data():
    domain = st.secrets["commcare"]["domain"]
    username = st.secrets["commcare"]["username"]
    api_key = st.secrets["commcare"]["api_key"]
    
    # Ensure URL is correct
    url = f"https://www.commcarehq.org/a/{domain}/api/v0.5/form/"
    
    # Adding headers can sometimes help if basic auth feels 'thin'
    # but the primary requirement is the correct auth tuple
    try:
        response = requests.get(
            url, 
            auth=(username, api_key),
            headers={"Content-Type": "application/json"}
        )
        
        # This will raise an error if 401 occurs, allowing us to catch it
        response.raise_for_status()
        
        data = response.json()
        df = pd.json_normalize(data.get("objects", []))
        return df
        
    except requests.exceptions.HTTPError as err:
        if response.status_code == 401:
            st.error("401 Unauthorized: Please check your Username (must be your full email) and API Key in secrets.toml.")
        else:
            st.error(f"HTTP Error: {err}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return pd.DataFrame()

# 3. Main Dashboard
df = get_commcare_data()

if not df.empty:
    # Look for username in typical locations
    possible_cols = ["metadata.username", "form.meta.username", "user_id"]
    user_col = next((col for col in possible_cols if col in df.columns), None)
    
    if user_col:
        st.subheader("Submissions per Enumerator")
        stats = df[user_col].value_counts().reset_index()
        stats.columns = ['Enumerator', 'Total Submissions']
        st.bar_chart(stats.set_index('Enumerator'))
        st.table(stats)
    else:
        st.write("Columns found:", df.columns.tolist())
        st.warning("Could not find a username column in the data.")
else:
    st.info("No data retrieved.")
