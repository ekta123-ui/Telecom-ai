import re
from datetime import date, timedelta

from sklearn.linear_model import LinearRegression
from sqlalchemy.orm import Session

from app.models.core import Subscription, UsageRecord, User
from app.models.telecom import RechargePlan


def _parse_data_per_day(value: str | None) -> float | None:
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
        .filter(
            Subscription.user_id == user.user_id,
            Subscription.is_active.is_(True),
        )
        .order_by(Subscription.start_date.desc())
        .first()
    )


def predict_usage(db: Session, user: User) -> dict:
    today = date.today()
    since = today - timedelta(days=59)
    records = (
        db.query(UsageRecord)
        .filter(
            UsageRecord.user_id == user.user_id,
            UsageRecord.usage_date >= since,
            UsageRecord.usage_date <= today,
        )
        .order_by(UsageRecord.usage_date.asc())
        .all()
    )

    if len(records) < 7:
        raise ValueError("At least 7 days of usage are needed to predict usage.")

    features = [
        [day_index, record.usage_date.weekday()]
        for day_index, record in enumerate(records)
    ]
    usage_values = [float(record.data_used_mb or 0) for record in records]

    model = LinearRegression()
    model.fit(features, usage_values)

    tomorrow = records[-1].usage_date + timedelta(days=1)
    predicted_tomorrow_mb = float(
        model.predict([[len(records), tomorrow.weekday()]])[0]
    )
    predicted_next_7_days_mb = sum(
        float(
            model.predict(
                [[len(records) + offset, (tomorrow + timedelta(days=offset)).weekday()]]
            )[0]
        )
        for offset in range(7)
    )
    average_daily_mb = sum(usage_values) / len(usage_values)
    slope = float(model.coef_[0])

    if slope > 0:
        trend = "increasing"
    elif slope < 0:
        trend = "decreasing"
    else:
        trend = "stable"

    result = {
        "average_daily_mb": round(average_daily_mb, 2),
        "predicted_tomorrow_mb": round(predicted_tomorrow_mb, 2),
        "predicted_next_7_days_mb": round(predicted_next_7_days_mb, 2),
        "trend": trend,
        "days_of_history": len(records),
    }

    subscription = _active_subscription(db, user)
    if subscription is None:
        return result

    plan = (
        db.query(RechargePlan)
        .filter(RechargePlan.plan_id == subscription.plan_id)
        .first()
    )
    if plan is None:
        return result

    total_data_mb = (
        float(subscription.data_limit_mb)
        if subscription.data_limit_mb is not None
        else None
    )
    if total_data_mb is None:
        data_per_day_mb = _parse_data_per_day(plan.data_per_day)
        if data_per_day_mb is not None:
            total_data_mb = data_per_day_mb * plan.validity_days

    if total_data_mb is None:
        return result

    used_since_start = (
        db.query(UsageRecord)
        .filter(
            UsageRecord.user_id == user.user_id,
            UsageRecord.usage_date >= subscription.start_date,
        )
        .all()
    )
    used_data_mb = sum(float(record.data_used_mb or 0) for record in used_since_start)
    remaining_mb = total_data_mb - used_data_mb
    days_until_data_runs_out = (
        remaining_mb / predicted_tomorrow_mb
        if predicted_tomorrow_mb > 0
        else None
    )

    result["remaining_mb"] = round(remaining_mb, 2)
    result["days_until_data_runs_out"] = (
        round(days_until_data_runs_out, 2)
        if days_until_data_runs_out is not None
        else None
    )
    days_left_in_plan = (subscription.end_date - today).days
    result["warning"] = (
        "Your data is estimated to run out before your plan ends."
        if days_until_data_runs_out is not None
        and days_until_data_runs_out < days_left_in_plan
        else None
    )
    return result
