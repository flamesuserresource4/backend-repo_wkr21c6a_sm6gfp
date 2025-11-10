import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict

from database import create_document
from schemas import Transaction, Prediction

app = FastAPI(title="Credit Card Fraud Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Credit Card Fraud Detection API is running"}

@app.get("/test")
def test_database():
    """Simple DB connectivity check"""
    response: Dict[str, Any] = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        from database import db
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

class PredictResponse(BaseModel):
    score: float
    label: str
    explanation: str
    stored_id: str | None = None

@app.post("/predict", response_model=PredictResponse)
def predict(transaction: Transaction):
    """
    Basic rule-based model returning a fraud probability and label.
    This is intentionally simple and runs without external ML dependencies.
    The request is validated by the Transaction schema.
    """
    risk = 0.0

    # Heuristic rules (simple demo scoring)
    risk += min(transaction.amount / 500.0, 1.0) * 0.25
    risk += min(transaction.distance_from_home / 1000.0, 1.0) * 0.1
    risk += min(transaction.distance_from_last_transaction / 500.0, 1.0) * 0.1
    risk += 0.1 if not transaction.repeat_retailer else 0
    risk += 0.1 if transaction.online_order else 0
    risk += 0.08 if not transaction.used_chip else 0
    risk += 0.08 if not transaction.used_pin_number else 0
    risk += 0.1 if transaction.international else 0
    risk += min(transaction.velocity_24h / 20.0, 1.0) * 0.19
    risk += 0.1 if transaction.hour in [0,1,2,3,4] else 0

    score = max(0.0, min(risk, 1.0))
    label = "Fraud" if score >= 0.5 else "Legit"

    # Short explanation
    reasons = []
    if transaction.amount > 500: reasons.append("high amount")
    if transaction.international: reasons.append("international")
    if transaction.online_order: reasons.append("online order")
    if not transaction.repeat_retailer: reasons.append("new merchant")
    if not transaction.used_chip: reasons.append("no chip")
    if not transaction.used_pin_number: reasons.append("no PIN")
    if transaction.velocity_24h > 5: reasons.append("high velocity")
    if transaction.distance_from_home > 200: reasons.append("far from home")
    if transaction.hour in [0,1,2,3,4]: reasons.append("night time")

    explanation = (
        f"Risk drivers: {', '.join(reasons)}" if reasons else "Low-risk pattern"
    )

    stored_id = None
    try:
        pred_doc = Prediction(
            transaction=transaction,
            score=score,
            label=label,
            explanation=explanation
        )
        stored_id = create_document("prediction", pred_doc)
    except Exception:
        # Database may be unavailable in some environments; continue without failing
        stored_id = None

    return PredictResponse(score=score, label=label, explanation=explanation, stored_id=stored_id)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
