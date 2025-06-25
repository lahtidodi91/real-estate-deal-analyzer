from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import math

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can change "*" to your GitHub domain for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class DealInput(BaseModel):
    address: str
    zip_code: str
    purchase_price: float
    down_payment: float
    interest_rate: Optional[float] = None  # Only used for loans
    term_years: Optional[int] = None
    monthly_rent: float
    strategy: str

    # Seller finance-specific
    seller_finance_interest_rate: Optional[float] = None
    seller_finance_term_years: Optional[int] = None
    balloon_payment: Optional[float] = None

@app.post("/analyze")
def analyze_deal(data: DealInput):
    expenses = 400  # placeholder for taxes/insurance/utilities/etc.
    noi = data.monthly_rent * 12 - expenses * 12

    if data.strategy == "subto":
        loan_amount = data.purchase_price - data.down_payment
        r = data.interest_rate / 100 / 12
        n = data.term_years * 12
        monthly_payment = loan_amount * r * (1 + r)**n / ((1 + r)**n - 1)

    elif data.strategy == "seller_finance":
        if not data.seller_finance_interest_rate or not data.seller_finance_term_years:
            raise HTTPException(status_code=400, detail="Missing seller finance loan terms.")
        loan_amount = data.purchase_price - data.down_payment
        r = data.seller_finance_interest_rate / 100 / 12
        n = data.seller_finance_term_years * 12
        monthly_payment = loan_amount * r * (1 + r)**n / ((1 + r)**n - 1)

        # Optional: balloon payment logic could go here

    else:
        raise HTTPException(status_code=400, detail="Unsupported strategy.")

    cash_flow = data.monthly_rent - monthly_payment - expenses

    return {
        "monthly_payment": round(monthly_payment, 2),
        "net_operating_income": round(noi, 2),
        "cash_flow": round(cash_flow, 2),
        "strategy": data.strategy
    }
