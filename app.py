import streamlit as st
import pandas as pd
from twilio.rest import Client

# 🎨 1. GLOBAL PAGE CONFIGURATION
st.set_page_config(
    page_title="HFC Central Dispatch", 
    page_icon="🛡️",
    layout="wide"
)

# 🔄 2. PERSISTENT MEMORY STORAGE
if "message_history" not in st.session_state: 
    st.session_state.message_history = []

# 🔐 3. CREDENTIAL VAULT PARSING
try:
    ACCOUNT_SID = st.secrets["TWILIO_ACCOUNT_SID"]
    AUTH_TOKEN = st.secrets["TWILIO_AUTH_TOKEN"]
    TWILIO_PHONE = st.secrets["TWILIO_NUMBER"]
except Exception:
    st.error("❌ Configuration Keys Missing. Please navigate to 'Advanced Settings > Secrets' in your Streamlit Cloud Dashboard and paste your Twilio credentials.")
    st.stop()

# 📊 4. HARDCODED ENTERPRISE DATA SYSTEM (Bypasses remote server network dependencies)
@st.cache_data
def get_hfc_records():
    return pd.DataFrame({
        'Error_ID': [1001, 1002, 1003, 1004, 1005],
        'Description': ['Incorrect currency mapping', 'Nested loop logic overflow', 'Inconsistent timestamp layout', 'Null value exception in processing', 'Tax math processing drift'],
        'Error_Type': ['Consistency', 'Logic', 'Consistency', 'Logic', 'Logic'],
        'Status': ['Corrected', 'Remaining', 'Corrected', 'Corrected', 'Remaining']
    })

df = get_hfc_records()

# --- INTERFACE PRESENTATION ---
st.title("🛡️ HFC Master Operation Center")
st.write("---")

# 📊 5. ANALYTICS CALCULATIONS
total_errors = len(df)
total_corrected = len(df[df['Status'].str.lower() == 'corrected'])
remaining = total_errors - total_corrected
consistency_count = len(df[df['Error_Type'].str.lower() == 'consistency'])
logic_count = len(df[df['Error_Type'].str.lower() == 'logic'])

st.subheader("📋 System Status Metrics")
m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
with m_col1: st.metric(label="Total Errors Identified", value=total_errors)
with m_col2: st.metric(label="Total Corrected Files", value=total_corrected, delta="Handled")
with m_col3: st.metric(label="Remaining Workload", value=remaining, delta=f"{remaining} Alert", delta_color="inverse")
with m_col4: st.metric(label="Consistency Conflicts", value=consistency_count)
with m_col5: st.metric(label="Logic Structural Errors", value=logic_count)

st.write("---")

# 🎛---- LAYOUT NAVIGATION TABS ----
dashboard_tab, dispatch_tab = st.tabs(["📂 Live Records Management", "📲 Remote Telecom Dispatcher"])

with dashboard_tab:
    st.subheader("Interactive Error Log Database Reference")
    
    # Simple Localized Filters
    selected_status = st.multiselect("Filter Records by Status:", options=df['Status'].unique(), default=df['Status'].unique())
    filtered_df = df[df['Status'].isin(selected_status)]
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

with dispatch_tab:
    st.subheader("Universal Communication Gateway Engine")
    
    gateway_mode = st.radio(
        "Select Gateway Protocol:",
        options=["Pure SMS Mode", "WhatsApp Sandbox Mode"],
        horizontal=True
    )
    
    c_col1, c_col2 = st.columns([1, 2])
    with c_col1:
        receiver = st.text_input("Recipient Targeted Phone Number", placeholder="09xxxxxxxx or +2519xxxxxxxx")
        st.caption("💡 Local formatting starting with '0' converts dynamically to international layout (+251).")
    with c_col2:
        message_body = st.text_area("Secure Payload Content", max_chars=160, placeholder="Type message notification update here...")

    # Action Logic Trigger
    if st.button("🚀 Transmit Communications Package", use_container_width=True):
        if not receiver or not message_body:
            st.warning("Action Interrupted: Target values require data payload entries.")
        else:
            # 🔧 Auto-formatting telephone variables
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

                    # Trigger Gateway Transmission
                    message = client.messages.create(body=message_body, from_=sender_id, to=target_id)
                    
                    # Log Transaction Session
                    st.session_state.message_history.append({
                        "Recipient Line": clean_receiver,
                        "Delivery Protocol": gateway_mode,
                        "Server Tracking SID Code": message.sid
                    })
                    st.success(f"✅ Secure Transmission Confirmed. Network SID: {message.sid}")
                except Exception as e:
                    st.error("❌ Gateway Execution Error: Transaction Rejected by Carrier Pipeline Architecture.")
                    st.exception(e)

    # Historical Logs Print Engine
    if st.session_state.message_history:
        st.write("---")
        st.write("### 🕒 Active Terminal Transmission Audit Logs")
        st.dataframe(st.session_state.message_history, use_container_width=True)
