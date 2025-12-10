from fastapi import FastAPI
import requests
import base64
import os
from dotenv import load_dotenv
from datetime import datetime


load_dotenv()

app = FastAPI()

consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")


def get_access_token():
    """ 
    Generate Mpesa access token 
    """
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth = (consumer_key, consumer_secret))

    json_response = response.json()
    return json_response["access_token"]


@app.post("/stk_push")
def stk_push(amount: int, phone: str):
    access_token = get_access_token()

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    shortcode = os.getenv("SHORTCODE")
    passkey = os.getenv("PASSKEY")

    # Generate password
    data_to_encode = shortcode + passkey + timestamp
    encoded_pass = base64.b64encode(data_to_encode.encode()).decode('utf-8')

    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    payload = {
        "BusinessShortCode": shortcode,
        "Password": encoded_pass,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,  # Customer phone number
        "PartyB": shortcode,
        "PhoneNumber": phone,
        "CallBackURL": os.getenv("CALLBACK_URL"),
        "AccountReference": "Test Payment",
        "TransactionDesc": "Payment"
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()

@app.post("/callback")
async def mpesa_callback(data: dict):
    print("Callback received:", data)
    return {"Result": "Callback received"}
