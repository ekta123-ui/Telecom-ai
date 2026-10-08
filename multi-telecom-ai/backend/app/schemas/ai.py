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
