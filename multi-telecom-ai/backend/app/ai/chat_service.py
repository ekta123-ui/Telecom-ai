import json
import uuid

from sqlalchemy.orm import Session

from app.ai.llm_service import generate_reply
from app.ai.intent_service import predict_intent
from app.ai.rag_service import retrieve_relevant_documents
from app.ai.tools import get_current_plan, get_data_balance, recommend_plans
from app.models.core import ChatHistory, User


SYSTEM_PROMPT = (
    "Answer only from the provided context. If the context is empty or does not "
    "answer the question, say \"I don't have that information\". Reply in the "
    "same language style as the user (English, Hindi, or Hinglish). Keep the "
    "answer under 120 words."
)


def _fallback(intent: str, tool_result: object, documents: list[dict]) -> str:
    if intent == "PLAN_RECOMMENDATION" and isinstance(tool_result, list):
        if not tool_result:
            return "I could not find a suitable plan based on your usage."
        return "Recommended plans: " + ", ".join(
            str(item["plan_name"]) for item in tool_result
        )
    if isinstance(tool_result, dict):
        if "message" in tool_result:
            return str(tool_result["message"])
        if intent == "DATA_BALANCE":
            return (
                f"Your average daily usage is {tool_result['average_daily_use_mb']} MB. "
                f"Estimated remaining daily data is "
                f"{tool_result['estimated_remaining_daily_mb']} MB."
            )
        if intent == "PLAN_DETAILS":
            return f"Your current plan is {tool_result.get('plan_name', 'not available')}."
    if documents:
        return documents[0]["content"]
    return "I don't have that information."


def _save_history(
    db: Session,
    user: User,
    session_id: uuid.UUID,
    role: str,
    message: str,
    intent: str,
    confidence: float,
    tool_used: str | None,
    sources: list[str],
) -> None:
    db.add(
        ChatHistory(
            user_id=user.user_id,
            session_id=session_id,
            role=role,
            message=message,
            intent=intent,
            confidence=confidence,
            tool_used=tool_used,
            sources={"titles": sources},
        )
    )


def handle_chat(
    db: Session,
    user: User,
    message: str,
    session_id: uuid.UUID,
) -> dict:
    intent, confidence = predict_intent(message)
    tool_used = None
    tool_result: object = None
    documents: list[dict] = []
    sources: list[str] = []

    if intent == "DATA_BALANCE":
        tool_used, tool_result = "get_data_balance", get_data_balance(db, user)
    elif intent == "PLAN_DETAILS":
        tool_used, tool_result = "get_current_plan", get_current_plan(db, user)
    elif intent == "PLAN_RECOMMENDATION":
        tool_used, tool_result = "recommend_plans", recommend_plans(db, user)
    elif intent in {"NETWORK_ISSUE", "BILL_QUERY", "GENERAL_SUPPORT"}:
        documents = retrieve_relevant_documents(message, db)
        sources = [str(document["title"]) for document in documents]
        tool_used = "retrieve_relevant_documents"

    if intent == "UNCLEAR":
        reply = "Please rephrase your question so I can help you better."
    elif intent in {"RECHARGE", "COMPLAINT", "COMPLAINT_STATUS", "PLAN_COMPARISON"}:
        reply = (
            "Please use the relevant Recharge, Complaint, Complaint Status, or "
            "Plan Comparison flow next so I can help with that request."
        )
    else:
        context_value = tool_result if tool_result is not None else documents
        context = json.dumps(context_value, default=str)
        reply = generate_reply(SYSTEM_PROMPT, message, context)
        if reply is None:
            reply = _fallback(intent, tool_result, documents)

    _save_history(
        db, user, session_id, "user", message, intent, confidence, tool_used, sources
    )
    _save_history(
        db, user, session_id, "assistant", reply, intent, confidence, tool_used, sources
    )
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    return {
        "reply": reply,
        "intent": intent,
        "confidence": confidence,
        "tool_used": tool_used,
        "sources": sources,
        "session_id": session_id,
    }
