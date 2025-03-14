def authenticate_gmail():
    """Authenticate with Gmail API using a local server flow."""
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

    # Start authentication flow
    flow = InstalledAppFlow.from_client_secrets_file("temp_credentials.json", SCOPES)

    try:
        creds = flow.run_local_server(port=0)  # Open browser and authenticate

        # Save credentials
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

        os.remove("temp_credentials.json")  # Remove temp file for security
        st.success("Authentication successful! Token saved.")

        return creds

    except Exception as e:
        st.error(f"Authentication failed: {str(e)}")

    return None
