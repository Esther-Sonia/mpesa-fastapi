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

@app