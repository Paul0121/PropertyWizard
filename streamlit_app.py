import streamlit as st
import requests
import re
import numpy as np
import os
from base64 import urlsafe_b64decode
import email
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import json

# ------------------------ AUTHENTICATION ------------------------
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

def authenticate_gmail():
    """Authenticate with OAuth 2.0 using Streamlit secrets."""
    credentials = {
        "installed": {
            "client_id": st.secrets["gmail"]["client_id"],
            "client_secret": st.secrets["gmail"]["client_secret"],
            "token_uri": st.secrets["gmail"]["token_uri"],
            "auth_uri": st.secrets["gmail"]["auth_uri"],
            "auth_provider_x509_cert_url": st.secrets["gmail"]["auth_provider_x509_cert_url"],
            "redirect_uris": json.loads(st.secrets["gmail"]["redirect_uris"])
        }
    }

    flow = InstalledAppFlow.from_client_config(credentials, SCOPES)
    creds = flow.run_local_server(port=0)
    service = build("gmail", "v1", credentials=creds)

    st.success("✅ Authentication successful! Gmail API is ready.")
    return service

# ------------------------ FETCH UNREAD EMAILS ------------------------
def get_unread_emails(service, max_results=5):
    """Fetch unread emails from Gmail."""
    try:
        results = service.users().messages().list(userId="me", labelIds=["INBOX"], q="is:unread", maxResults=max_results).execute()
        messages = results.get("messages", [])
        return messages
    except Exception as e:
        st.error(f"Error fetching emails: {e}")
        return []

def extract_email_body(service, message_id):
    """Extract the plain text body from an email."""
    try:
        message = service.users().messages().get(userId="me", id=message_id, format="raw").execute()
        msg_str = urlsafe_b64decode(message["raw"]).decode("utf-8")
        msg = email.message_from_string(msg_str)

        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    return part.get_payload(decode=True).decode()
        else:
            return msg.get_payload(decode=True).decode()
    except Exception as e:
        st.error(f"Error extracting email body: {e}")
        return None

# ------------------------ EXTRACT PROPERTY DETAILS ------------------------
def extract_property_details(email_body):
    """Extract address, bedrooms, and bathrooms from email content using regex."""
    address_pattern = r"\d{1,5}\s[\w\s]+,\s\w{2}\s\d{5}"  # Example: "123 Main St, FL 33701"
    bed_bath_pattern = r"(\d+)\s*(?:bed|br).*?(\d+)\s*(?:bath|ba)"  # Example: "3 bed 2 bath"

    address_match = re.search(address_pattern, email_body)
    bed_bath_match = re.search(bed_bath_pattern, email_body, re.IGNORECASE)

    address = address_match.group(0) if address_match else None
    bedrooms = int(bed_bath_match.group(1)) if bed_bath_match else None
    bathrooms = int(bed_bath_match.group(2)) if bed_bath_match else None

    return address, bedrooms, bathrooms

# ------------------------ FETCH COMPS & CALCULATE MAO ------------------------
def fetch_comps(address, bedrooms, bathrooms):
    """Fetch comparable properties from Zillow/Redfin (scraping or API)."""
    zillow_url = f"https://www.zillow.com/homes/{address.replace(' ', '-')}_rb/"
    response = requests.get(zillow_url)

    if response.status_code == 200:
        # Extract comparable properties (this part depends on your scraper)
        comps = extract_comps(response.text)  # Implement extract_comps()
        
        if comps:
            arv = np.mean([comp["price_per_sqft"] * comp["sqft"] for comp in comps])
            return comps, arv
    return None, None

def calculate_mao(arv, repair_costs=30000):
    """Calculate the Max Allowable Offer using the 60% ARV formula."""
    return (arv * 0.6) - repair_costs

# ------------------------ PROCESS EMAILS ------------------------
def process_emails(service):
    """Fetch unread emails, extract property details, run comps, and send results."""
    messages = get_unread_emails(service)

    for msg in messages:
        email_body = extract_email_body(service, msg["id"])
        if email_body:
            address, bedrooms, bathrooms = extract_property_details(email_body)
            if address and bedrooms and bathrooms:
                st.write(f"Extracted: {address}, {bedrooms} beds, {bathrooms} baths")
                
                comps, arv = fetch_comps(address, bedrooms, bathrooms)
                if comps:
                    mao = calculate_mao(arv)
                    send_email_with_results(service, address, comps, mao)
                    st.success(f"✅ Property meets criteria! Email sent with MAO: ${mao:,.2f}")
                else:
                    mark_email_as_read(service, msg["id"])
                    st.warning(f"⚠️ No comps found for {address}. Email marked as read.")
            else:
                st.warning("⚠️ No property details found in this email.")

# ------------------------ SEND EMAIL WITH RESULTS ------------------------
def send_email_with_results(service, address, comps, mao):
    """Send an email with the comps and MAO calculation."""
    subject = f"Property Analysis: {address}"
    body = f"Comparable Properties:\n{comps}\n\nMAO: ${mao:,.2f}"
    
    message = f"Subject: {subject}\n\n{body}"
    
    # Send email (this part depends on how you send emails via Gmail API)
    print("🚀 Email sent!")  # Replace with actual send logic

# ------------------------ MARK EMAIL AS READ ------------------------
def mark_email_as_read(service, message_id):
    """Mark an email as read if it does not meet criteria."""
    try:
        service.users().messages().modify(userId="me", id=message_id, body={"removeLabelIds": ["UNREAD"]}).execute()
        st.info("📩 Email marked as read.")
    except Exception as e:
        st.error(f"Error marking email as read: {e}")

# ------------------------ STREAMLIT UI ------------------------
st.title("Automated Property Comps System")

if st.button("Run Email Processing"):
    service = authenticate_gmail()
    if service:
        process_emails(service)
    else:
        st.warning("⚠️ Authentication failed.")
