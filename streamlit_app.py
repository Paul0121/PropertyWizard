import streamlit as st
import pickle
import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

def authenticate_gmail():
    """Authenticate with Gmail API using a verification code."""
    creds = None

    # Load credentials from Streamlit Secrets
    credentials_json = {
        "installed": {
            "client_id": st.secrets["gmail"]["client_id"],
            "project_id": st.secrets["gmail"]["project_id"],
            "auth_uri": st.secrets["gmail"]["auth_uri"],
            "token_uri": st.secrets["gmail"]["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["gmail"]["auth_provider_x509_cert_url"],
            "client_secret": st.secrets["gmail"]["client_secret"],
            "redirect_uris": [st.secrets["gmail"]["redirect_uris"]]
        }
    }

    # Save to a temporary JSON file
    with open("temp_credentials.json", "w") as f:
        json.dump(credentials_json, f)

    # Authenticate using manual verification code
    flow = InstalledAppFlow.from_client_secrets_file("temp_credentials.json", SCOPES)
    creds = flow.run_console()  # Uses a console-based authentication method

    # Save the credentials
    with open("token.pickle", "wb") as token:
        pickle.dump(creds, token)

    os.remove("temp_credentials.json")  # Remove temp file for security

    return creds

# Streamlit UI
st.title("Gmail Authentication for Property Emails")

if st.button("Authenticate Gmail"):
    creds = authenticate_gmail()
    if creds:
        st.success("Authentication successful! Token saved.")
    else:
        st.error("Authentication failed. Please try again.")
