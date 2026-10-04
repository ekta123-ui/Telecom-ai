from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.core import Subscription, User
from app.models.telecom import Provider, RechargePlan
from app.routes.users import get_current_user
from app.schemas.telecom import CurrentSubscriptionOut

router = APIRouter(prefix="/api/subscriptions", tags=["subscriptions"])


@router.get("/current", response_model=CurrentSubscriptionOut)
def current_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sub = (
        db.query(Subscription)
        .filter(Subscription.user_id == current_user.user_id, Subscription.is_active == True)  # noqa: E712
        .order_by(Subscription.start_date.desc())
        .first()
    )
    if not sub:
        raise HTTPException(status_code=404, detail="No active subscription found")

    plan = db.query(RechargePlan).filter(RechargePlan.plan_id == sub.plan_id).first()
    provider = db.query(Provider).filter(Provider.provider_id == sub.provider_id).first()

    return CurrentSubscriptionOut(
        subscription_id=sub.subscription_id,
        provider_name=provider.provider_name,
        plan_name=plan.plan_name,
        price=plan.price,
        data_per_day=plan.data_per_day,
        start_date=sub.start_date,
        end_date=sub.end_date,
        days_remaining=(sub.end_date - date.today()).days,
    )