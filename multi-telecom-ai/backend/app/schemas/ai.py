from pydantic import BaseModel
from uuid import UUID


class IntentRequest(BaseModel):
    text: str


class IntentResponse(BaseModel):
    intent: str
    confidence: float
    is_confident: bool


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
    sources: list[str]
    has_answer: bool


class ChatRequest(BaseModel):
    message: str
    session_id: UUID | None = None


class ChatResponse(BaseModel):
    reply: str
    intent: str
    confidence: float
    tool_used: str | None
    sources: list[str]
    session_id: UUID


class UsagePredictionResponse(BaseModel):
    average_daily_mb: float
    predicted_tomorrow_mb: float
    predicted_next_7_days_mb: float
    trend: str
    days_of_history: int
    remaining_mb: float | None = None
    days_until_data_runs_out: float | None = None
    warning: str | None = None
