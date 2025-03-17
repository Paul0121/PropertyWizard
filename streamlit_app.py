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
