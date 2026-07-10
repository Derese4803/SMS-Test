import streamlit as st
import urllib.parse

# 🎨 App Window Setup
st.set_page_config(page_title="Quick SMS Linker", page_icon="💬", layout="centered")

st.title("💬 Quick SMS Linker")
st.write("Type a number and message to instantly generate a local SMS dispatch link.")
st.write("---")

# 📝 User Inputs
receiver = st.text_input("Recipient Phone Number", placeholder="09xxxxxxxx or +2519xxxxxxxx")
message_body = st.text_area("SMS Text Content", max_chars=160, placeholder="Type your text update here...")

# 🚀 Processing Logic
if receiver and message_body:
    # Auto-format local number to global standard (+251)
    clean_receiver = receiver.strip().replace(" ", "")
    if clean_receiver.startswith('0'):
        clean_receiver = '+251' + clean_receiver[1:]
    elif clean_receiver.startswith('251') and not clean_receiver.startswith('+'):
        clean_receiver = '+' + clean_receiver

    # URL encode the message text so spaces and characters don't break the link
    encoded_message = urllib.parse.quote(message_body)
    
    # Standard universal SMS URI format
    sms_url = f"sms:{clean_receiver}?body={encoded_message}"
    
    st.write("---")
    st.info(f"Target: {clean_receiver}")
    
    # Display a direct system action link
    st.markdown(
        f'<a href="{sms_url}" target="_blank" style="text-decoration:none;">'
        f'<div style="background-color:#00cc66;color:white;padding:12px;text-align:center;border-radius:8px;font-weight:bold;font-size:16px;">'
        f'💬 Open Native Messaging App to Send'
        f'</div></a>', 
        unsafe_allow_html=True
    )
else:
    st.warning("Please provide both a phone number and message payload to generate the transmission link.")
