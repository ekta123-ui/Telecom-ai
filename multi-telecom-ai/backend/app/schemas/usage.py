from datetime import date

from pydantic import BaseModel, ConfigDict


class UsageRecordOut(BaseModel):
    usage_date: date
    data_used_mb: float
    call_minutes: int
    sms_count: int

    model_config = ConfigDict(from_attributes=True)


class UsageSummary(BaseModel):
    total_days: int
    total_data_mb: float
    average_daily_mb: float
    average_daily_gb: float
    records: list[UsageRecordOut]