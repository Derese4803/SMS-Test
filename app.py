import streamlit as st
import pandas as pd
import requests
import base64
import io
from twilio.rest import Client

# 🎨 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="HFC Core Dashboard", 
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🔄 2. INITIALIZE SHARED STATE (For amnesia prevention across reruns)
if "logged_in_as" not in st.session_state: 
    st.session_state.logged_in_as = "Admin"
if "message_history" not in st.session_state: 
    st.session_state.message_history = []

# 🔐 3. LOAD CREDENTIAL SECTOR SECURELY
try:
    # GitHub Token (Optional fallback allowed)
    GITHUB_TOKEN = st.secrets["github"]["token"] if "github" in st.secrets else None
    
    # Twilio Communication Credentials (Strictly required for Dispatcher tab)
    ACCOUNT_SID = st.secrets["TWILIO_ACCOUNT_SID"]
    AUTH_TOKEN = st.secrets["TWILIO_AUTH_TOKEN"]
    TWILIO_PHONE = st.secrets["TWILIO_NUMBER"]
except Exception:
    st.error("❌ Critical Secret Missing: Verify that your local `.streamlit/secrets.toml` file contains all required GitHub and Twilio keys.")
    st.stop()

# 🌐 4. GITHUB DATA RETRIEVAL PIPELINE
def fetch_from_github(filename):
    try:
        if not GITHUB_TOKEN:
            return None
        url = f"https://api.github.com/repos/Derese4803/HFC/contents/{filename}?ref=main"
        headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            return pd.read_csv(io.StringIO(base64.b64decode(res.json()['content']).decode('utf-8')))
        return None
    except Exception:
        return None

def load_placeholder_data():
    return pd.DataFrame({
        'Error_ID': [1001, 1002, 1003, 1004, 1005],
        'Description': ['Incorrect currency mapping', 'Nested loop logic overflow', 'Inconsistent timestamp layout', 'Null value exception in processing', 'Tax math processing drift'],
        'Error_Type': ['Consistency', 'Logic', 'Consistency', 'Logic', 'Logic'],
        'Status': ['Corrected', 'Remaining', 'Corrected', 'Corrected', 'Remaining']
    })

# --- DATA INGESTION EXECUTION ---
FILENAME = "hfc_data.csv"
df = fetch_from_github(FILENAME)
is_mock = False

if df is None:
    df = load_placeholder_data()
    is_mock = True

# --- MAIN GRAPHICAL USER INTERFACE ---
st.title("🛡️ HFC Master Operation Center")
if is_mock:
    st.warning("⚠️ Running on Local Simulation Engine. Live remote GitHub repository tracking is offline.")
else:
    st.success(f"🌐 Secure Connection Established: Tracking remote dataset `{FILENAME}` in real-time.")

st.write("---")

# 📊 5. METRIC COMPUTATION & PRESENTATION
try:
    total_errors = len(df)
    total_corrected = len(df[df['Status'].str.lower() == 'corrected'])
    remaining = total_errors - total_corrected
    consistency_count = len(df[df['Error_Type'].str.lower() == 'consistency'])
    logic_count = len(df[df['Error_Type'].str.lower() == 'logic'])
except KeyError as e:
    st.error(f"❌ Structural Schema Error: Your data file is missing the required column classification: {e}")
    st.stop()

st.subheader("📋 Administrative System Metrics")
m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
with m_col1: st.metric(label="Total Errors", value=total_errors)
with m_col2: st.metric(label="Total Corrected", value=total_corrected, delta="Handled")
with m_col3: st.metric(label="Remaining Workload", value=remaining, delta=f"{remaining} Alert", delta_color="inverse")
with m_col4: st.metric(label="Consistency Conflicts", value=consistency_count)
with m_col5: st.metric(label="Logic Errors", value=logic_count)

st.write("---")

# 🎛️ 6. LAYOUT TABS DIVISION
dashboard_tab, dispatch_tab = st.tabs(["📂 Live Records Management", "📲 Remote Telecom Dispatcher"])

with dashboard_tab:
    st.subheader("Interactive Error Log Reference")
    
    # Sidebar Filters (Instantly triggers execution redraws)
    st.sidebar.header("🔍 Global Log Filters")
    st.sidebar.write(f"Logged Identity: **{st.session_state.logged_in_as}**")
    
    selected_status = st.sidebar.multiselect("Filter by Status:", options=df['Status'].unique(), default=df['Status'].unique())
    selected_type = st.sidebar.multiselect("Filter by Category Type:", options=df['Error_Type'].unique(), default=df['Error_Type'].unique())
    
    # Filter Execution
    filtered_df = df[(df['Status'].isin(selected_status)) & (df['Error_Type'].isin(selected_type))]
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

with dispatch_tab:
    st.subheader("Universal Communication Gateway Engine")
    
    gateway_mode = st.radio(
        "Choose Telecommunication Delivery Pipeline Option:",
        options=["Pure SMS Mode", "WhatsApp Sandbox Mode"],
        horizontal=True
    )
    
    c_col1, c_col2 = st.columns([1, 2])
    with c_col1:
        receiver = st.text_input("Recipient Targeted Device Line", placeholder="09xxxxxxxx or +2519xxxxxxxx")
        st.caption("💡 Local numbers starting with '0' automatically convert to standard international format (+251).")
    with c_col2:
        message_body = st.text_area("Secure Message Transmission Content Payload", max_chars=160, placeholder="Type message text here...")

    # Action Dispatch button deployment 
    if st.button("🚀 Transmit Communications Package", use_container_width=True):
        if not receiver or not message_body:
            st.warning("Transaction Aborted: Input fields require full identification data formatting.")
        else:
            # 🔧 Country Code Auto-formatting (+251 replacement logic)
            clean_receiver = receiver.strip().replace(" ", "")
            if clean_receiver.startswith('0'):
                clean_receiver = '+251' + clean_receiver[1:]
            elif clean_receiver.startswith('251') and not clean_receiver.startswith('+'):
                clean_receiver = '+' + clean_receiver
                
            with st.spinner("Authorizing credentials packet with Twilio routing matrices..."):
                try:
                    client = Client(ACCOUNT_SID, AUTH_TOKEN)
                    
                    if gateway_mode == "WhatsApp Sandbox Mode":
                        sender_id = f"whatsapp:{TWILIO_PHONE}"
                        target_id = f"whatsapp:{clean_receiver}"
                    else:
                        sender_id = TWILIO_PHONE
                        target_id = clean_receiver

                    # Trigger remote communication request execution call
                    message = client.messages.create(body=message_body, from_=sender_id, to=target_id)
                    
                    # Store to dynamic in-memory audit logs
                    st.session_state.message_history.append({
                        "Recipient Line": clean_receiver,
                        "Delivery Protocol": gateway_mode,
                        "Server Tracking SID Code": message.sid
                    })
                    st.success(f"✅ Secure Transmission Confirmed. Network SID: {message.sid}")
                except Exception as e:
                    st.error("❌ Gateway Execution Error: Transaction Rejected by Carrier Pipeline Architecture.")
                    st.exception(e)

    # Render History Logs if they exist
    if st.session_state.message_history:
        st.write("---")
        st.write("### 🕒 Active Terminal Transmission Audit Logs")
        st.dataframe(st.session_state.message_history, use_container_width=True)
