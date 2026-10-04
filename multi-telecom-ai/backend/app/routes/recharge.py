import secrets
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.core import Recharge, Subscription, User
from app.models.telecom import Provider, RechargePlan
from app.routes.users import get_current_user
from app.schemas.recharge import RechargeHistoryItem, RechargeRequest, RechargeResponse

router = APIRouter(prefix="/api/recharge", tags=["recharge"])


def generate_transaction_id() -> str:
    return f"TXN{date.today().strftime('%Y%m%d')}{secrets.token_hex(4).upper()}"


@router.post("", response_model=RechargeResponse, status_code=201)
def do_recharge(
    payload: RechargeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    plan = db.query(RechargePlan).filter(
        RechargePlan.plan_id == payload.plan_id,
        RechargePlan.provider_id == payload.provider_id,
    ).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found for this provider")

    provider = db.query(Provider).filter(Provider.provider_id == payload.provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    # Simulated payment — always succeeds
    recharge = Recharge(
        user_id=current_user.user_id,
        provider_id=payload.provider_id,
        plan_id=payload.plan_id,
        mobile_number=payload.mobile_number,
        amount=plan.price,
        payment_method="SIMULATED",
        status="SUCCESS",
        transaction_id=generate_transaction_id(),
    )
    db.add(recharge)

    # Deactivate any existing active subscription for this mobile number
    db.query(Subscription).filter(
        Subscription.user_id == current_user.user_id,
        Subscription.mobile_number == payload.mobile_number,
        Subscription.is_active == True,  # noqa: E712
    ).update({"is_active": False})

    # Create the new active subscription
    subscription = Subscription(
        user_id=current_user.user_id,
        provider_id=payload.provider_id,
        plan_id=payload.plan_id,
        mobile_number=payload.mobile_number,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=plan.validity_days),
        is_active=True,
    )
    db.add(subscription)

    db.commit()
    db.refresh(recharge)

    return RechargeResponse(
        recharge_id=recharge.recharge_id,
        transaction_id=recharge.transaction_id,
        amount=float(recharge.amount),
        status=recharge.status,
        plan_name=plan.plan_name,
        provider_name=provider.provider_name,
        validity_days=plan.validity_days,
        created_at=recharge.created_at,
    )


@router.get("/history", response_model=list[RechargeHistoryItem])
def recharge_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(Recharge)
        .filter(Recharge.user_id == current_user.user_id)
        .order_by(Recharge.created_at.desc())
        .all()
    )