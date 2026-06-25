from pydantic import BaseModel, Field
from uuid import UUID
from datetime import date
from decimal import Decimal

# --- SACCO SCHEMAS ---
class SaccoCreate(BaseModel):
    sacco_name: str = Field(..., min_length=3, max_length=100, examples=["Ganji Sacco"])

class SaccoResponse(BaseModel):
    sacco_id: UUID
    sacco_name: str
    
    class Config:
        from_attributes = True

# --- VEHICLE OWNER SCHEMAS ---
class OwnerCreate(BaseModel):
    sacco_id: UUID
    owner_name: str = Field(..., min_length=2, max_length=100)
    phone_number: str = Field(..., examples=["+254712345678"])

class OwnerResponse(BaseModel):
    owner_id: UUID
    sacco_id: UUID
    owner_name: str
    phone_number: str

    class Config:
        from_attributes = True

# --- DAILY LEDGER SCHEMAS ---
class LedgerCreate(BaseModel):
    sacco_id: UUID
    owner_id: UUID
    registration_number: str = Field(..., max_length=15, examples=["KAA 123A"])
    cash_collected: Decimal = Field(default=0.00)
    mpesa_collected: Decimal = Field(default=0.00)
    total_expenses: Decimal = Field(default=0.00)

class LedgerResponse(BaseModel):
    ledger_id: UUID
    sacco_id: UUID
    owner_id: UUID
    registration_number: str
    operating_date: date
    cash_collected: Decimal
    mpesa_collected: Decimal
    total_expenses: Decimal
    sacco_fee_deducted: Decimal
    is_finalized: bool
    sms_sent: bool
    is_extended: bool

    class Config:
        from_attributes = True