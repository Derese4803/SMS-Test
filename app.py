import streamlit as st
import urllib.parse

# 🎨 1. APPLICATION VIEWPORT SETUP
st.set_page_config(
    page_title="HFC Local Messenger", 
    page_icon="💬", 
    layout="centered"
)

st.title("💬 HFC Local Messenger")
st.write("Generate zero-token instant SMS triggers for mobile devices.")
st.write("---")

# 📝 2. USER DATA INPUT INTERFACE
receiver = st.text_input("Target Phone Number", placeholder="09xxxxxxxx or +2519xxxxxxxx")
st.caption("💡 Local formatting starting with '0' converts dynamically to international layout (+251).")

message_body = st.text_area("SMS Text Content", max_chars=160, placeholder="Type message notation update here...")

# 🚀 3. COMPILATION LOGIC SECTOR
if receiver and message_body:
    # Remove any accidential spacing user input errors
    clean_receiver = receiver.strip().replace(" ", "")
    
    # Auto-formatting telephone variables to Ethiopian Telecom global layouts (+251)
    if clean_receiver.startswith('0'):
        clean_receiver = '+251' + clean_receiver[1:]
    elif clean_receiver.startswith('251') and not clean_receiver.startswith('+'):
        clean_receiver = '+' + clean_receiver

    # URL encode text strings so special characters/spaces don't break web paths
    encoded_message = urllib.parse.quote(message_body)
    
    # Compile universal device OS pipeline link
    sms_link = f"sms:{clean_receiver}?body={encoded_message}"
    
    st.write("---")
    st.info(f"🎯 Target Queue: {clean_receiver}")
    
    # Render native device trigger block injection
    st.markdown(
        f'<a href="{sms_link}" target="_blank" style="text-decoration:none;">'
        f'<div style="background-color:#00cc66;color:white;padding:14px;text-align:center;border-radius:8px;font-weight:bold;font-size:16px;box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">'
        f'💬 Open Phone App & Send'
        f'</div></a>', 
        unsafe_allow_html=True
    )
    st.caption("📱 **Mobile device compatibility:** Clicking this button seamlessly opens your phone's native Message app with the phone number and text pre-filled.")
else:
    st.warning("⚠️ Input fields empty: Please populate both targets to generate link configuration.")
