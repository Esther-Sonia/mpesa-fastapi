from fastapi import FastAPI
import requests
import base64
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")


def get_access_token():
    key_secret = f"{consumer_key}:{consumer_secret}".encode("ascii")
    b64_encoded_key = base64.b64encode(key_secret).decode("ascii")

    headers = {