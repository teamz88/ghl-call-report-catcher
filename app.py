#!/usr/bin/env python3
"""
Simple Email Retrieval Script for Security Code Emails
"""

import json
import logging
import requests
import re
from msal import ConfidentialClientApplication

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Hard-coded configuration
CONFIG = {
    "client_id": "b30804b0-********",
    "client_secret": "l5U8Q~******",
    "authority": "https://login.microsoftonline.com/*********tenant_id",
    "scope": ["https://graph.microsoft.com/.default"],
    "username": "info@omadligroup.com"
}

# Target email senders and subject
TARGET_SENDERS = [
    "noreply@mg.tidyyourhomes.com",
    "noreply@mailbox.gohighlevel.com"
]
TARGET_SUBJECT = "Login security code"

def authenticate():
    """Authenticate with Microsoft Graph API"""
    app = ConfidentialClientApplication(
        client_id=CONFIG['client_id'],
        client_credential=CONFIG['client_secret'],
        authority=CONFIG['authority']
    )
    
    result = app.acquire_token_for_client(scopes=CONFIG['scope'])
    
    if "access_token" in result:
        logger.info("Authentication successful")
        return result['access_token']
    else:
        logger.error(f"Authentication failed: {result.get('error_description', 'Unknown error')}")
        return None

def get_security_code_emails(access_token):
    """Get security code emails from specific senders"""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Get last 20 emails without complex filtering
    endpoint = f"https://graph.microsoft.com/v1.0/users/{CONFIG['username']}/messages"
    
    params = {
        '$orderby': 'receivedDateTime desc',
        '$top': 20,
        '$expand': 'attachments'
    }
    
    logger.info("Getting last 20 emails...")
    
    try:
        response = requests.get(endpoint, headers=headers, params=params)
        response.raise_for_status()
        result = response.json()
        
        if 'value' in result:
            all_emails = result['value']
            logger.info(f"Retrieved {len(all_emails)} emails")
            
            # Filter in Python
            filtered_emails = []
            for email in all_emails:
                from_addr = email.get('from', {}).get('emailAddress', {}).get('address', '').lower()
                subject = email.get('subject', '')
                
                # Check if from specific senders and has target subject
                if (from_addr in [sender.lower() for sender in TARGET_SENDERS] and 
                    subject == TARGET_SUBJECT):
                    filtered_emails.append(email)
            
            logger.info(f"Found {len(filtered_emails)} security code emails after filtering")
            return filtered_emails
        else:
            logger.warning("No emails found")
            return []
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to retrieve emails: {e}")
        return []

def extract_otp_code(text):
    """Extract 6-digit OTP code from email body"""
    if not text:
        return None
    
    # Multiple patterns to match different OTP formats
    patterns = [
        r'security code[:\s]*(\d{6})',  # "security code: 123456"
        r'login code[:\s]*(\d{6})',     # "login code: 123456"
        r'verification code[:\s]*(\d{6})', # "verification code: 123456"
        r'code[:\s]*(\d{6})',           # "code: 123456"
        r'(\d{6})',                     # any 6 digits
    ]
    
    text_lower = text.lower()
    
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            return match.group(1)
    
    return None

def save_to_reports_json(emails):
    """Save emails to reports.json file with only required fields and extracted OTP"""
    try:
        # Extract only required fields
        simplified_emails = []
        for email in emails:
            body_preview = email.get('bodyPreview', '')
            otp_code = extract_otp_code(body_preview)
            
            simplified_email = {
                "receivedDateTime": email.get('receivedDateTime', ''),
                "subject": email.get('subject', ''),
                "bodyPreview": body_preview,
                "senderEmail": email.get('from', {}).get('emailAddress', {}).get('address', ''),
                "otpCode": otp_code
            }
            simplified_emails.append(simplified_email)
        
        with open('reports.json', 'w', encoding='utf-8') as f:
            json.dump(simplified_emails, f, indent=2, ensure_ascii=False, default=str)
        logger.info(f"Saved {len(simplified_emails)} emails to reports.json")
        print(f"✅ Successfully saved {len(simplified_emails)} emails to reports.json")
        
        # Show extracted OTP codes
        for i, email in enumerate(simplified_emails, 1):
            if email['otpCode']:
                print(f"  📱 Email {i}: OTP Code = {email['otpCode']}")
            else:
                print(f"  ❌ Email {i}: No OTP code found")
                
    except Exception as e:
        logger.error(f"Failed to save to reports.json: {e}")
        print(f"❌ Failed to save emails: {e}")

def get_latest_otp():
    """Get only the latest OTP code from security emails"""
    try:
        # Get authentication token
        token = authenticate()
        if not token:
            return None
        
        # Get security code emails
        emails = get_security_code_emails(token)
        if not emails:
            print("❌ No security code emails found")
            return None
        
        # Sort emails by received date (newest first)
        emails.sort(key=lambda x: x.get('receivedDateTime', ''), reverse=True)
        
        # Get the latest email
        latest_email = emails[0]
        body_preview = latest_email.get('bodyPreview', '')
        otp_code = extract_otp_code(body_preview)
        
        if otp_code:
            print(f"✅ Latest OTP code found: {otp_code}")
            print(f"📧 From: {latest_email.get('from', {}).get('emailAddress', {}).get('address', '')}")
            print(f"📅 Received: {latest_email.get('receivedDateTime', '')}")
            return otp_code
        else:
            print("❌ No OTP code found in the latest email")
            return None
            
    except Exception as e:
        logger.error(f"Failed to get latest OTP: {e}")
        print(f"❌ Error getting latest OTP: {e}")
        return None

def main():
    """Main function - get latest OTP code only"""
    print("🔍 Getting latest OTP code from security emails...")
    
    latest_otp = get_latest_otp()
    
    if latest_otp:
        print(f"\n🎯 LATEST OTP: {latest_otp}")
        return latest_otp
    else:
        print("\n❌ No OTP code found")
        return None

if __name__ == "__main__":
    main()