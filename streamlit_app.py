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

# Authenticate and get the Gmail service
service = authenticate_gmail()

def get_latest_emails(service, query=""):
    """Fetch the latest emails matching the query."""
    if not service:
        st.error("⚠️ Gmail service is not available. Please authenticate first.")
        return []

    try:
        results = service.users().messages().list(userId="me", q=query, maxResults=5).execute()
        messages = results.get("messages", [])

        if not messages:
            st.warning("No emails found matching your query.")
            return []

        email_data = []
        for msg in messages:
            msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
            headers = msg_data["payload"]["headers"]

            # Extract subject and sender
            subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
            sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")
            
            # Extract email body
            body = msg_data["snippet"]  # Snippet gives a short preview

            email_data.append({"sender": sender, "subject": subject, "body": body})

        return email_data

    except Exception as e:
        st.error(f"Error fetching emails: {str(e)}")
        return []

# Streamlit UI to Fetch Emails
st.header("📬 Fetch Latest Property Emails")

if st.button("Get Latest Emails"):
    if service:
        emails = get_latest_emails(service, query="real estate deal OR property listing")
        if emails:
            for email in emails:
                st.subheader(f"📧 {email['subject']}")
                st.write(f"**From:** {email['sender']}")
                st.write(f"**Preview:** {email['body']}")
        else:
            st.warning("No relevant emails found.")
    else:
        st.error("⚠️ Authentication failed. Please refresh the app and try again.")
