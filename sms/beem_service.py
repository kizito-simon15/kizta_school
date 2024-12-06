import requests
import base64
import logging
from .models import SentSMS
from django.conf import settings

API_KEY = "15ac6c603b676f61"
SECRET_KEY = "YzBhZGUyMzk2NDY5YjBkMzAxZmQ2MDdhYTM4NjljZTY2NTU2MGIxNTUxY2ZkZjE3NDZiNDE3MDBiNDM0MDBlMw=="
BASE_URL = "https://apisms.beem.africa"
SOURCE_ADDR = "ELEMENTS"

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_auth_header():
    token = f"{API_KEY}:{SECRET_KEY}"
    encoded_token = base64.b64encode(token.encode()).decode()
    return f"Basic {encoded_token}"

def send_sms(message, recipients):
    url = f"{BASE_URL}/v1/send"
    formatted_recipients = [{"recipient_id": i + 1, "dest_addr": recipient["dest_addr"]} for i, recipient in enumerate(recipients)]
    data = {
        "source_addr": SOURCE_ADDR,
        "schedule_time": "",
        "encoding": 0,
        "message": message,
        "recipients": formatted_recipients
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": get_auth_header()
    }
    response = requests.post(url, json=data, headers=headers)
    try:
        response_json = response.json()
        logger.debug(f"send_sms response: {response_json}")

        if response.status_code == 200 and response_json.get('successful'):
            # Save each sent SMS to the SentSMS model once
            unique_recipients = {recipient['dest_addr']: recipient for recipient in recipients}.values()
            for recipient in unique_recipients:
                SentSMS.objects.create(
                    dest_addr=recipient['dest_addr'],
                    first_name=recipient.get('first_name'),
                    last_name=recipient.get('last_name'),
                    message=message,
                    network=response_json.get('network', 'Unknown'),
                    length=len(message),
                    sms_count=(len(message) // 160) + 1,  # Calculate SMS count based on message length
                    status='Sent'
                )
        return response_json
    except ValueError:
        logger.error(f"send_sms error: {response.text}")
        return {"error": "Invalid response from server"}

def check_balance():
    url = f"{BASE_URL}/public/v1/vendors/balance"
    headers = {
        "Content-Type": "application/json",
        "Authorization": get_auth_header()
    }
    response = requests.get(url, headers=headers)
    try:
        response_json = response.json()
        logger.debug(f"check_balance response: {response_json}")
        return response_json
    except ValueError:
        logger.error(f"check_balance error: {response.text}")
        return {"error": "Invalid response from server"}

def get_sms_history():
    url = f"{BASE_URL}/public/v1/sms/history"  # Replace with actual endpoint if available
    headers = {
        "Content-Type": "application/json",
        "Authorization": get_auth_header()
    }
    response = requests.get(url, headers=headers)
    try:
        response_json = response.json()
        logger.debug(f"get_sms_history response: {response_json}")
        return response_json
    except ValueError:
        logger.error(f"get_sms_history error: {response.text}")
        return {"error": "Invalid response from server"}
