from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Integer)
    phone_number = Column(String)
    mpesa_receipt = Column(String)
    result_code = Column(Integer)
    result_desc = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
