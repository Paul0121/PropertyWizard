import streamlit as st
import pickle
import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def authenticate_gmail():
    """Authenticate using OAuth for personal Gmail accounts."""
    creds = None

    # Load credentials from Streamlit secrets
    credentials_json = {
        "installed": {
            "client_id": st.secrets["gmail"]["client_id"],
            "client_secret": st.secrets["gmail"]["client_secret"],
            "auth_uri": st.secrets["gmail"]["auth_uri"],
            "token_uri": st.secrets["gmail"]["token_uri"],
            "redirect_uris": st.secrets["gmail"]["redirect_uris"]
        }
    }

    # Save credentials to a temporary file
    with open("temp_credentials.json", "w") as f:
        json.dump(credentials_json, f)

    # Start authentication flow
    flow = InstalledAppFlow.from_client_secrets_file("temp_credentials.json", SCOPES)
    auth_url, _ = flow.authorization_url(prompt="consent")

    # Show login link in Streamlit
    st.write("### Step 1: Click the link below to authenticate:")
    st.markdown(f"[Authenticate with Google]({auth_url})", unsafe_allow_html=True)

    # Step 2: Enter the authorization code
    auth_code = st.text_input("### Step 2: Paste the authorization code here:")

    if auth_code:
        try:
            # Fetch credentials using the entered authorization code
            flow.fetch_token(code=auth_code)
            creds = flow.credentials

            # Save credentials for future use
            with open("token.pickle", "wb") as token:
                pickle.dump(creds, token)

            os.remove("temp_credentials.json")  # Remove temp file for security
            st.success("✅ Authentication successful! Token saved.")
            return creds
        except Exception as e:
            st.error(f"❌ Authentication failed: {str(e)}")
    
    return None

# Streamlit UI
st.title("Gmail Authentication for Personal Accounts")

if st.button("Authenticate Gmail"):
    creds = authenticate_gmail()
    if creds:
        st.success("🎉 You're authenticated!")
    else:
        st.warning("⚠️ Please enter the authorization code after clicking the link.")
