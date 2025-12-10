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

@app.post("/stkpush/")
def stk_push(amount: int, phone_number: str):
    """ 
    Initiate STK Push request 
    """
    access_token = get_access_token()
    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    business_short_code = os.getenv("BUSINESS_SHORT_CODE")
    passkey = os.getenv("PASSKEY")
    password_str = business_short_code + passkey + timestamp
    password = base64.b64encode(password_str.encode()).decode()

    payload = {
        "BusinessShortCode": business_short_code,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": business_short_code,
        "PhoneNumber": phone_number,
        "CallBackURL": os.getenv("CALLBACK_URL"),
        "AccountReference": "TestPayment",
        "TransactionDesc": "Payment of X"
    }

    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()