from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.core import UsageRecord, User
from app.routes.users import get_current_user
from app.schemas.usage import UsageSummary

router = APIRouter(prefix="/api/usage", tags=["usage"])


@router.get("/summary", response_model=UsageSummary)
def usage_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    records = (
        db.query(UsageRecord)
        .filter(UsageRecord.user_id == current_user.user_id)
        .order_by(UsageRecord.usage_date.desc())
        .limit(30)
        .all()
    )
    total_data = sum(r.data_used_mb for r in records) or 0
    days = len(records) or 1
    avg_mb = total_data / days

    return UsageSummary(
        total_days=len(records),
        total_data_mb=round(total_data, 2),
        average_daily_mb=round(avg_mb, 2),
        average_daily_gb=round(avg_mb / 1024, 2),
        records=records,
    )