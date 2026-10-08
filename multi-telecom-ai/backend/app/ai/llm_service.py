import httpx

from app.config import settings


def generate_reply(system_prompt: str, user_message: str, context: str) -> str | None:
    payload = {
        "model": settings.ollama_model,
        "system": system_prompt,
        "prompt": f"Context:\n{context or '(empty)'}\n\nUser message:\n{user_message}",
        "stream": False,
    }
    try:
        response = httpx.post(
            f"{settings.ollama_base_url.rstrip('/')}/api/generate",
            json=payload,
            timeout=30.0,
        )
        response.raise_for_status()
        reply = response.json().get("response")
        return reply.strip() if isinstance(reply, str) and reply.strip() else None
    except (httpx.HTTPError, ValueError, TypeError, AttributeError):
        return None
