from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID  # <-- THIS WAS THE MISSING KEY INDEPENDENT IMPORT!

from app.database import get_db
from app.models import Sacco, VehicleOwner, DailyLedger
from app.schemas import SaccoCreate, SaccoResponse, OwnerCreate, OwnerResponse, LedgerCreate, LedgerResponse

router = APIRouter()

# 1. ENDPOINT: REGISTER A NEW SACCO
@router.post("/saccos", response_model=SaccoResponse, status_code=status.HTTP_201_CREATED)
async def register_sacco(sacco_data: SaccoCreate, db: AsyncSession = Depends(get_db)):
    # Check if a Sacco with this name already exists
    query = select(Sacco).where(Sacco.sacco_name == sacco_data.sacco_name)
    result = await db.execute(query)
    existing_sacco = result.scalar_one_or_none()
    
    if existing_sacco:
        raise HTTPException(status_code=400, detail="Sacco name already registered!")
    
    # Create and save new Sacco record
    new_sacco = Sacco(sacco_name=sacco_data.sacco_name)
    db.add(new_sacco)
    await db.commit()
    await db.refresh(new_sacco)
    return new_sacco

# 2. ENDPOINT: REGISTER A VEHICLE OWNER
@router.post("/owners", response_model=OwnerResponse, status_code=status.HTTP_201_CREATED)
async def register_owner(owner_data: OwnerCreate, db: AsyncSession = Depends(get_db)):
    # 1. Verify that the parent Sacco exists first (Foreign Key Integrity Check)
    sacco_query = select(Sacco).where(Sacco.sacco_id == owner_data.sacco_id)
    sacco_result = await db.execute(sacco_query)
    if not sacco_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Parent Sacco ID not found!")
    
    # 2. Create the owner
    new_owner = VehicleOwner(
        sacco_id=owner_data.sacco_id,
        owner_name=owner_data.owner_name,
        phone_number=owner_data.phone_number
    )
    db.add(new_owner)
    await db.commit()
    await db.refresh(new_owner)
    return new_owner

# 3. ENDPOINT: CREATE A DAILY VEHICLE RUN LEDGER
@router.post("/ledgers", response_model=LedgerResponse, status_code=status.HTTP_201_CREATED)
async def create_ledger(ledger_data: LedgerCreate, db: AsyncSession = Depends(get_db)):
    # Rule Check 1: Ensure the Sacco exists
    sacco_check = await db.execute(select(Sacco).where(Sacco.sacco_id == ledger_data.sacco_id))
    if not sacco_check.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Sacco not found!")

    # Rule Check 2: Ensure the Owner exists (Crucial Guardrail)
    owner_check = await db.execute(select(VehicleOwner).where(VehicleOwner.owner_id == ledger_data.owner_id))
    if not owner_check.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Vehicle Owner not found! Operational ledger blocked.")

    # Create the ledger record (the default 500 KES fee applies automatically)
    new_ledger = DailyLedger(
        sacco_id=ledger_data.sacco_id,
        owner_id=ledger_data.owner_id,
        registration_number=ledger_data.registration_number.upper(),
        cash_collected=ledger_data.cash_collected,
        mpesa_collected=ledger_data.mpesa_collected,
        total_expenses=ledger_data.total_expenses
    )
    
    db.add(new_ledger)
    await db.commit()
    await db.refresh(new_ledger)
    return new_ledger

# 4. ENDPOINT: GET DAILY FINANCIAL SUMMARY FOR A SACCO
@router.get("/saccos/{sacco_id}/summary", status_code=status.HTTP_200_OK)
async def get_sacco_summary(sacco_id: UUID, db: AsyncSession = Depends(get_db)):
    # 1. Verify Sacco exists
    sacco_check = await db.execute(select(Sacco).where(Sacco.sacco_id == sacco_id))
    sacco = sacco_check.scalar_one_or_none()
    if not sacco:
        raise HTTPException(status_code=404, detail="Sacco not found!")

    # 2. Fetch all ledgers tied to this Sacco
    ledger_query = select(DailyLedger).where(DailyLedger.sacco_id == sacco_id)
    ledger_result = await db.execute(ledger_query)
    ledgers = ledger_result.scalars().all()

    # 3. Compute running totals
    total_gross = 0.00
    total_expenses = 0.00
    total_fees_collected = 0.00
    active_vehicles = len(ledgers)

    for ledger in ledgers:
        total_gross += float(ledger.cash_collected + ledger.mpesa_collected)
        total_expenses += float(ledger.total_expenses)
        total_fees_collected += float(ledger.sacco_fee_deducted)

    net_owner_payout = total_gross - total_expenses - total_fees_collected

    return {
        "sacco_name": sacco.sacco_name,
        "active_vehicles_reported": active_vehicles,
        "total_gross_revenue": total_gross,
        "total_operational_expenses": total_expenses,
        "total_sacco_debe_collected": total_fees_collected,
        "net_payout_to_owners": net_owner_payout
    }