from datetime import date

from pydantic import BaseModel, ConfigDict


class PlanOut(BaseModel):
    plan_id: int
    provider_id: int
    plan_name: str
    price: int
    data_per_day: str | None
    validity_days: int
    unlimited_calls: str | None
    sms_per_day: int | None
    ott_benefits: str | None
    plan_category: str | None

    model_config = ConfigDict(from_attributes=True)


class ProviderOut(BaseModel):
    provider_id: int
    provider_name: str
    network_type: str | None
    coverage_score: float | None

    model_config = ConfigDict(from_attributes=True)


class CurrentSubscriptionOut(BaseModel):
    subscription_id: int
    provider_name: str
    plan_name: str
    price: int
    data_per_day: str | None
    start_date: date
    end_date: date
    days_remaining: int

    model_config = ConfigDict(from_attributes=True)