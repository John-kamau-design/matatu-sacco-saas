import uuid
from datetime import date
from sqlalchemy import Column, String, Numeric, Boolean, Date, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from .database import Base

# 1. THE SACCO TABLE
class Sacco(Base):
    __tablename__ = "saccos"
    
    sacco_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sacco_name = Column(String(100), nullable=False)
    created_at = Column(Date, server_default=text("CURRENT_DATE"))

# 2. THE VEHICLE OWNERS TABLE
class VehicleOwner(Base):
    __tablename__ = "vehicle_owners"
    
    owner_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sacco_id = Column(UUID(as_uuid=True), ForeignKey("saccos.sacco_id", ondelete="CASCADE"), nullable=False)
    owner_name = Column(String(100), nullable=False)
    phone_number = Column(String(15), nullable=False)

# 3. THE VEHICLES & DAILY OPERATIONS LEDGER
class DailyLedger(Base):
    __tablename__ = "daily_ledgers"
    
    ledger_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sacco_id = Column(UUID(as_uuid=True), ForeignKey("saccos.sacco_id", ondelete="CASCADE"), nullable=False)
    
    # Enforcing our absolute business rule: Vehicle CANNOT exist without an owner!
    owner_id = Column(UUID(as_uuid=True), ForeignKey("vehicle_owners.owner_id", ondelete="RESTRICT"), nullable=False)
    
    registration_number = Column(String(15), nullable=False)
    operating_date = Column(Date, default=date.today)
    
    # Daily Operational Numbers (Cleared per trip loop)
    cash_collected = Column(Numeric(10, 2), default=0.00)
    mpesa_collected = Column(Numeric(10, 2), default=0.00)
    total_expenses = Column(Numeric(10, 2), default=0.00)
    sacco_fee_deducted = Column(Numeric(10, 2), default=500.00) # Daily "Debe"
    
    # State Control Gates
    is_finalized = Column(Boolean, default=False)
    sms_sent = Column(Boolean, default=False)
    
    # Late Night Extension Flag (+2 hours)
    is_extended = Column(Boolean, default=False)