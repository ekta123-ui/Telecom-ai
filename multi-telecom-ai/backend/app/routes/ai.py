import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.ai.chat_service import handle_chat
from app.ai.intent_service import predict_intent
from app.ai.rag_service import retrieve_relevant_documents
from app.database import get_db
from app.routes.users import get_current_user
from app.schemas.ai import (
    AskRequest,
    AskResponse,
    ChatRequest,
    ChatResponse,
    IntentRequest,
    IntentResponse,
)
from app.models.core import User


router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.post("/intent", response_model=IntentResponse)
def classify_intent(request: IntentRequest) -> IntentResponse:
    intent, confidence = predict_intent(request.text)
    return IntentResponse(
        intent=intent,
        confidence=confidence,
        is_confident=intent != "UNCLEAR",
    )


@router.post("/ask", response_model=AskResponse)
def ask_knowledge_base(
    request: AskRequest,
    db: Session = Depends(get_db),
) -> AskResponse:
    documents = retrieve_relevant_documents(request.question, db)
    if not documents:
        return AskResponse(
            answer="I don't have information on that in my knowledge base.",
            sources=[],
            has_answer=False,
        )

    return AskResponse(
        answer=documents[0]["content"],
        sources=[document["title"] for document in documents],
        has_answer=True,
    )


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatResponse:
    session_id = request.session_id or uuid.uuid4()
    return ChatResponse(**handle_chat(db, current_user, request.message, session_id))
