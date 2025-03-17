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
import requests
import numpy as np

def fetch_comps(address, bedrooms, bathrooms):
    """Fetch comparable properties from Zillow/Redfin (scraping or API)."""
    
    # Replace this with your actual Zillow scraper function
    zillow_url = f"https://www.zillow.com/homes/{address.replace(' ', '-')}_rb/"
    response = requests.get(zillow_url)
    
    if response.status_code == 200:
        # Extract comparable properties (this part depends on your scraper)
        comps = extract_comps(response.text)
        
        # Compute ARV using average price per square foot
        arv = np.mean([comp["price_per_sqft"] * comp["sqft"] for comp in comps])
        
        return comps, arv
    else:
        return None, None

def calculate_mao(arv, repair_costs=30000):
    """Calculate the Max Allowable Offer using the 60% ARV formula."""
    return (arv * 0.6) - repair_costs

# Example Usage:
address = "2313 W Saint Isabel St"
bedrooms = 3
bathrooms = 2

comps, arv = fetch_comps(address, bedrooms, bathrooms)
if comps:
    mao = calculate_mao(arv)
    print(f"ARV: ${arv:,.2f}, MAO: ${mao:,.2f}")
    print(f"Comparable Properties: {comps}")
else:
    print("No comps found.")

import re
from googleapiclient.discovery import build
from base64 import urlsafe_b64decode
import email

def get_unread_emails(service, max_results=5):
    """Fetch unread emails from Gmail."""
    try:
        results = service.users().messages().list(userId="me", labelIds=["INBOX"], q="is:unread", maxResults=max_results).execute()
        messages = results.get("messages", [])
        return messages
    except Exception as e:
        print(f"Error fetching emails: {e}")
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
        print(f"Error extracting email body: {e}")
        return None

def extract_property_details(email_body):
    """Extract address, bedrooms, and bathrooms from email content using regex."""
    address_pattern = r"\d{1,5}\s[\w\s]+,\s\w{2}\s\d{5}"  # Matches "123 Main St, FL 33701"
    bed_bath_pattern = r"(\d+)\s*(?:bed|br).*?(\d+)\s*(?:bath|ba)"  # Matches "3 bed 2 bath" or "3br 2ba"

    address_match = re.search(address_pattern, email_body)
    bed_bath_match = re.search(bed_bath_pattern, email_body, re.IGNORECASE)

    address = address_match.group(0) if address_match else None
    bedrooms = int(bed_bath_match.group(1)) if bed_bath_match else None
    bathrooms = int(bed_bath_match.group(2)) if bed_bath_match else None

    return address, bedrooms, bathrooms

# Example usage
def process_emails(service):
    messages = get_unread_emails(service)

    for msg in messages:
        email_body = extract_email_body(service, msg["id"])
        if email_body:
            address, bedrooms, bathrooms = extract_property_details(email_body)
            if address and bedrooms and bathrooms:
                print(f"Extracted: {address}, {bedrooms} beds, {bathrooms} baths")
                return address, bedrooms, bathrooms
            else:
                print("No property details found in this email.")

    return None, None, None
