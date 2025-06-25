from fastapi import FastAPI, Request
from pydantic import BaseModel
import requests
import os

app = FastAPI()

class PropertyData(BaseModel):
    address: str
    zip_code: str
    purchase_price: float
    down_payment: float
    interest_rate: float
    term_years: int
    monthly_rent: float
    strategy: str  # "subto" or "seller_finance"

@app.post("/analyze")
def analyze_deal(data: PropertyData):
    monthly_payment = (
        (data.purchase_price - data.down_payment)
        * (data.interest_rate / 100 / 12)
        / (1 - (1 + data.interest_rate / 100 / 12) ** (-data.term_years * 12))
    )

    # Simple NOI Calculation
    gross_income = data.monthly_rent * 12
    expenses = gross_income * 0.35  # basic assumption
    noi = gross_income - expenses

    return {
        "monthly_payment": round(monthly_payment, 2),
        "net_operating_income": round(noi, 2),
        "cash_flow": round(data.monthly_rent - monthly_payment, 2),
        "strategy": data.strategy,
    }
