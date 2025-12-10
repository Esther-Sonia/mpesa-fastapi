from fastapi import FastAPI
import requests
import base64
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

co