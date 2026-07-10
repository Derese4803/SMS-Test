import streamlit as st
from twilio.rest import Client

# 🎨 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="HFC Dispatch Gateway", 
    page_icon="📲", 
    layout="centered"
)

# 🔄 2. INITIALIZE SHARED STATE
if "logged_in_as" not in st.session_state: 
    st.session_state.logged_in_as = "Admin"  # Defaulting to Admin for testing
if "message_history" not in st.session_state: 
    st.session_state.message_history = []

# 🔐 3. LOAD CREDENTIALS
try:
    ACCOUNT_SID = st.secrets["TWILIO_ACCOUNT_SID"]
    AUTH_TOKEN = st.secrets["TWILIO_AUTH_TOKEN"]
    TWILIO_PHONE = st.secrets["TWILIO_NUMBER"]
except Exception:
    st.error("❌ Configuration Error: Please verify that `.streamlit/secrets.toml` is correctly configured.")
    st.stop()

# 🎛️ 4. SIDEBAR CONTROLS
st.sidebar.header("⚙️ Gateway Settings")
st.sidebar.write(f"👤 User: **{st.session_state.logged_in_as}**")

# Channel Router: Toggle between standard SMS and WhatsApp to bypass regional blocks
gateway_mode = st.sidebar.radio(
    "Select Delivery Channel:",
    options=["Pure SMS Mode", "WhatsApp Sandbox Mode"],
    help="If local carriers block trial SMS verifications, toggle to WhatsApp Sandbox Mode."
)

st.sidebar.write("---")
st.sidebar.subheader("📜 Session Logs")
st.sidebar.write(f"Total dispatched: {len(st.session_state.message_history)}")

# 📝 5. MAIN APPLICATION UI
st.title("📲 HFC Universal Dispatch Gateway")
st.write("Send instant alerts or corrections directly to recipient devices.")
st.write("---")

# Inform the user based on selected mode
if gateway_mode == "WhatsApp Sandbox Mode":
    st.info("ℹ️ **WhatsApp Mode Active**: Ensure your recipient phone number has joined your Twilio Sandbox by texting your sandbox keyword to your Twilio number.")
else:
    st.warning("⚠️ **SMS Mode Active**: For Twilio trial accounts, the recipient number must be verified via Voice Call in your Twilio Console.")

# Form Fields
receiver = st.text_input("Recipient Phone Number", placeholder="+251911xxxxxx or +1415xxxxxxx")
st.caption("Always prefix the number with its international country code (e.g., +251 for Ethiopia).")

message_body = st.text_area("Message Content", placeholder="Type your text update here...", max_chars=160)

# 🚀 6. DISPATCH LOGIC
if st.button("🚀 Execute Remote Dispatch", use_container_width=True):
    if not receiver or not message_body:
        st.warning("Please populate both target number and content payload fields.")
    else:
        with st.spinner("Routing communication payload through Twilio matrix..."):
            try:
                # Fire up the Twilio Engine
                client = Client(ACCOUNT_SID, AUTH_TOKEN)
                
                # Apply channel formatting adjustments based on UI toggle switch
                if gateway_mode == "WhatsApp Sandbox Mode":
                    sender_id = f"whatsapp:{TWILIO_PHONE}"
                    target_id = f"whatsapp:{receiver}"
                else:
                    sender_id = TWILIO_PHONE
                    target_id = receiver

                # Trigger API Call
                message = client.messages.create(
                    body=message_body,
                    from_=sender_id,
                    to=target_id
                )
                
                # Update Session State Tracker
                st.session_state.message_history.append({
                    "to": receiver,
                    "channel": gateway_mode,
                    "sid": message.sid
                })
                
                st.success(f"✅ Dispatch Successful! Tracking ID: {message.sid}")
                
            except Exception as e:
                st.error(f"❌ Transaction Terminated by Gateway Engine.")
                st.exception(e)

# 🕒 7. RECENT HISTORY FOOTER
if st.session_state.message_history:
    st.write("---")
    st.subheader("📋 Recent Transmission Audit Trail")
    st.dataframe(st.session_state.message_history, use_container_width=True)
