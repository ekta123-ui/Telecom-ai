import re
from datetime import date, timedelta
from sqlalchemy.orm import Session

from app.models.core import Subscription, UsageRecord, User
from app.models.telecom import RechargePlan


def _number_from_data_per_day(value: str | None) -> float | None:
    if not value:
        return None
    match = re.search(r"(\d+(?:\.\d+)?)\s*(gb|mb)", value, re.IGNORECASE)
    if not match:
        return None
    amount = float(match.group(1))
    return amount * 1024 if match.group(2).lower() == "gb" else amount


def _active_subscription(db: Session, user: User) -> Subscription | None:
    return (
        db.query(Subscription)
        .filter(Subscription.user_id == user.user_id, Subscription.is_active.is_(True))
        .order_by(Subscription.end_date.desc())
        .first()
    )


def _usage_average(db: Session, user: User) -> tuple[float, float]:
    since = date.today() - timedelta(days=29)
    records = (
        db.query(UsageRecord)
        .filter(
            UsageRecord.user_id == user.user_id,
            UsageRecord.usage_date >= since,
        )
        .all()
    )
    total_mb = sum(float(record.data_used_mb or 0) for record in records)
    days = max((date.today() - since).days + 1, 1)
    return total_mb, total_mb / days


def get_data_balance(db: Session, user: User) -> dict:
    subscription = _active_subscription(db, user)
    if subscription is None:
        return {"has_subscription": False, "message": "No active subscription found."}

    plan = db.query(RechargePlan).filter(RechargePlan.plan_id == subscription.plan_id).first()
    total_used_mb, average_daily_use_mb = _usage_average(db, user)
    plan_daily_mb = _number_from_data_per_day(plan.data_per_day if plan else None)
    remaining_daily_mb = (
        max(plan_daily_mb - average_daily_use_mb, 0)
        if plan_daily_mb is not None
        else None
    )
    return {
        "has_subscription": True,
        "plan_name": plan.plan_name if plan else None,
        "data_per_day": plan.data_per_day if plan else None,
        "total_used_last_30_days_mb": round(total_used_mb, 2),
        "average_daily_use_mb": round(average_daily_use_mb, 2),
        "estimated_remaining_daily_mb": (
            round(remaining_daily_mb, 2) if remaining_daily_mb is not None else None
        ),
        "subscription_end_date": subscription.end_date,
    }


def get_current_plan(db: Session, user: User) -> dict:
    subscription = _active_subscription(db, user)
    if subscription is None:
        return {"has_subscription": False, "message": "No active subscription found."}
    plan = db.query(RechargePlan).filter(RechargePlan.plan_id == subscription.plan_id).first()
    if plan is None:
        return {"has_subscription": True, "plan_found": False, "plan_id": subscription.plan_id}
    return {
        "has_subscription": True,
        "plan_found": True,
        "plan_id": plan.plan_id,
        "plan_name": plan.plan_name,
        "price": plan.price,
        "data_per_day": plan.data_per_day,
        "validity_days": plan.validity_days,
        "unlimited_calls": plan.unlimited_calls,
        "sms_per_day": plan.sms_per_day,
        "ott_benefits": plan.ott_benefits,
        "plan_category": plan.plan_category,
        "subscription_end_date": subscription.end_date,
    }


def recommend_plans(
    db: Session,
    user: User,
    budget: float | None = None,
) -> list[dict]:
    _, average_daily_use_mb = _usage_average(db, user)
    query = db.query(RechargePlan)
    if budget is not None:
        query = query.filter(RechargePlan.price <= budget)

    candidates = []
    for plan in query.all():
        plan_daily_mb = _number_from_data_per_day(plan.data_per_day)
        if plan_daily_mb is None or plan_daily_mb < average_daily_use_mb:
            continue
        candidates.append(
            (
                abs(plan_daily_mb - average_daily_use_mb),
                {
                    "plan_id": plan.plan_id,
                    "plan_name": plan.plan_name,
                    "price": plan.price,
                    "data_per_day": plan.data_per_day,
                    "validity_days": plan.validity_days,
                    "reason": (
                        f"Provides {plan.data_per_day} per day, close to your "
                        f"average use of {average_daily_use_mb:.2f} MB per day."
                    ),
                },
            )
        )
    candidates.sort(key=lambda item: item[0])
    return [item[1] for item in candidates[:3]]
