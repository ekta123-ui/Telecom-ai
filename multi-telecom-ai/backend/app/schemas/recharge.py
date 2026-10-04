from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RechargeRequest(BaseModel):
    provider_id: int
    plan_id: int
    mobile_number: str


class RechargeResponse(BaseModel):
    recharge_id: int
    transaction_id: str
    amount: float
    status: str
    plan_name: str
    provider_name: str
    validity_days: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RechargeHistoryItem(BaseModel):
    recharge_id: int
    transaction_id: str
    amount: float
    status: str
    plan_id: int
    provider_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)