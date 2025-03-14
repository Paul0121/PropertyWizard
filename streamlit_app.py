import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

def authenticate_gmail():
    """Authenticate with Gmail API using a Service Account."""
    creds = Credentials.from_service_account_info(st.secrets["gmail"])

    try:
        service = build("gmail", "v1", credentials=creds)
        st.success("✅ Authentication successful! Gmail API is ready.")
        return service
    except Exception as e:
        st.error(f"❌ Authentication failed: {str(e)}")
        return None

# Streamlit UI
st.title("Gmail API Authentication (Service Account)")

if st.button("Connect to Gmail"):
    service = authenticate_gmail()
    if service:
        st.success("🎉 You're authenticated!")
    else:
        st.warning("⚠️ Failed to authenticate.")
