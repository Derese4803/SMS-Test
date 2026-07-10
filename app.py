import streamlit as st
from twilio.rest import Client

# 🎨 App Window Setup
st.set_page_config(page_title="SMS Dispatch", page_icon="💬", layout="centered")

st.title("💬 Pure SMS Dispatcher")
st.write("Send instant text alerts across global mobile networks.")
st.write("---")

# 🔐 Pull Credentials from Streamlit Cloud Secrets
try:
    ACCOUNT_SID = st.secrets["TWILIO_ACCOUNT_SID"]
    AUTH_TOKEN = st.secrets["TWILIO_AUTH_TOKEN"]
    TWILIO_PHONE = st.secrets["TWILIO_NUMBER"]
except Exception:
    st.error("❌ Setup Missing: Please paste your TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_NUMBER into your Streamlit Advanced Settings -> Secrets.")
    st.stop()

# 📝 User Inputs
receiver = st.text_input("Recipient Phone Number", placeholder="09xxxxxxxx or +2519xxxxxxxx")
st.caption("💡 Local formatting starting with '0' converts dynamically to international layout (+251).")

message_body = st.text_area("SMS Text Content", max_chars=160, placeholder="Type message notification update here...")

# 🚀 Action Logic Trigger
if st.button("🚀 Transmit SMS Now", use_container_width=True):
    if not receiver or not message_body:
        st.warning("Action Interrupted: Both phone number and text content are required.")
    else:
        # 🔧 Clean and Auto-format the phone number for global routing
        clean_receiver = receiver.strip().replace(" ", "")
        if clean_receiver.startswith('0'):
            clean_receiver = '+251' + clean_receiver[1:]
        elif clean_receiver.startswith('251') and not clean_receiver.startswith('+'):
            clean_receiver = '+' + clean_receiver
            
        with st.spinner("Routing message through telecom carrier networks..."):
            try:
                # Fire up the Twilio Engine
                client = Client(ACCOUNT_SID, AUTH_TOKEN)
                
                # Execute direct SMS delivery call
                message = client.messages.create(
                    body=message_body,
                    from_=TWILIO_PHONE,
                    to=clean_receiver
                )
                
                st.success(f"✅ SMS Transmitted Successfully! Network Tracking ID: {message.sid}")
                
            except Exception as e:
                st.error("❌ Gateway Execution Error: Transaction Rejected by Carrier Pipeline.")
                st.exception(e)
