from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
import requests, base64, os
from dotenv import load_dotenv
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from sqlalchemy import insert
from models import Base, Payment


load_dotenv()

app = FastAPI()

DATABASE_URL = "sqlite+aiosqlite:///./payments.db"
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")

def get_access_token():
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=(consumer_key, consumer_secret))
    return response.json()["access_token"]

@app.post("/stk_push")
def stk_push(amount: int, phone: str):
    access_token = get_access_token()
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    shortcode = os.getenv("SHORTCODE")
    passkey = os.getenv("PASSKEY")
    encoded_pass = base64.b64encode(f"{shortcode}{passkey}{timestamp}".encode()).decode('utf-8')
    
    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {"Authorization": f"Bearer {access_token}"}
    payload = {
        "BusinessShortCode": shortcode,
        "Password": encoded_pass,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": shortcode,
        "PhoneNumber": phone,
        "CallBackURL": os.getenv("CALLBACK_URL"),
        "AccountReference": "Test Payment",
        "TransactionDesc": "Payment"
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

@app.get("/payments")
async def get_payments():
    async with async_session() as session:
        result = await session.execute(select(Payment))
        payments = result.scalars().all()
        return [
            {
                "id": p.id,
                "amount": p.amount,
                "phone_number": p.phone_number,
                "mpesa_receipt": p.mpesa_receipt,
                "result_code": p.result_code,
                "result_desc": p.result_desc,
                "timestamp": p.timestamp.isoformat()
            } for p in payments
        ]

@app.post("/callback")
async def mpesa_callback(request: Request):
    try:
        data = await request.json()
    except Exception:
        
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Invalid or empty JSON received"}
        )

    stk_callback = data.get("Body", {}).get("stkCallback", {})
    result_code = stk_callback.get("ResultCode")
    result_desc = stk_callback.get("ResultDesc")
    merchant_request_id = stk_callback.get("MerchantRequestID")
    checkout_request_id = stk_callback.get("CheckoutRequestID")
    amount = None
    phone_number = None
    mpesa_receipt = None

    callback_metadata = stk_callback.get("CallbackMetadata", {}).get("Item", [])
    for item in callback_metadata:
        name = item.get("Name")
        value = item.get("Value")
        if name == "Amount":
            amount = value
        elif name == "MpesaReceiptNumber":
            mpesa_receipt = value
        elif name == "PhoneNumber":
            phone_number = value

    async with async_session() as session: 
        async with session.begin():
            stmt = insert(Payment).values(
                amount=amount,
                phone_number=phone_number,
                mpesa_receipt=mpesa_receipt,
                result_code=result_code,
                result_desc=result_desc,
            )
            await session.execute(stmt)

    return {"ResultCode": 0, "ResultDesc": "Accepted"}
