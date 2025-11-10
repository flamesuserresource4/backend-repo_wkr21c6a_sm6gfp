"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Add your own schemas here:
# --------------------------------------------------

class Transaction(BaseModel):
    """
    Transactions collection schema
    Collection: "transaction"
    """
    amount: float = Field(..., ge=0, description="Transaction amount in USD")
    merchant: str = Field(..., description="Merchant name")
    category: str = Field(..., description="Merchant category")
    distance_from_home: float = Field(..., ge=0, description="Distance from cardholder's home (km)")
    distance_from_last_transaction: float = Field(..., ge=0, description="Distance from previous transaction (km)")
    repeat_retailer: bool = Field(..., description="Has the user shopped here before")
    used_chip: bool = Field(..., description="Chip used for card-present transactions")
    used_pin_number: bool = Field(..., description="PIN used for authentication")
    online_order: bool = Field(..., description="Transaction made online")
    hour: int = Field(..., ge=0, le=23, description="Hour of day in 24h format")
    age: int = Field(..., ge=16, le=120, description="Cardholder age")
    international: bool = Field(..., description="Is the merchant international")
    velocity_24h: int = Field(..., ge=0, description="Number of transactions in last 24 hours")

class Prediction(BaseModel):
    """
    Predictions collection schema
    Collection: "prediction"
    """
    transaction: Transaction
    score: float = Field(..., ge=0, le=1, description="Fraud probability score between 0 and 1")
    label: str = Field(..., description="Predicted label: 'Fraud' or 'Legit'")
    explanation: str = Field(..., description="Short explanation of the decision")
