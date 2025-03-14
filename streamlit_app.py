import streamlit as st
import pickle
import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

def authenticate_gmail():
    """Authenticate with Gmail API using manual code entry."""
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

            # Save credentials
            with open("token.pickle", "wb") as token:
                pickle.dump(creds, token)

            os.remove("temp_credentials.json")  # Remove temp file for security
            st.success("✅ Authentication successful! Token saved.")

            return creds
        except Exception as e:
            st.error(f"❌ Authentication failed: {str(e)}")
    
    return None

# Streamlit UI
st.title("Gmail Authentication for Property Emails")

if st.button("Authenticate Gmail"):
    creds = authenticate_gmail()
    if creds:
        st.success("🎉 You're authenticated!")
    else:
        st.warning("⚠️ Please

                   if __name__ == "__main__":
    import os
    os.system("streamlit run streamlit_app.py")

