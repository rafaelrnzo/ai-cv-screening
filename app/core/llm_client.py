import httpx
from app.core.config import settings

def _approx_tokens(s: str) -> int:
    return max(1, len(s) // 4)

def build_llm_request(system_prompt: str, user_prompt: str) -> dict:
    input_est = _approx_tokens(system_prompt) + _approx_tokens(user_prompt)
    room = max(1,settings.MODEL_CTX_WINDOW - input_est - settings.SAFETY_BUFFER)
    allowed = max(64, min(settings.HARD_CAP_MAX_NEW, room))
    return {
        "model": settings.VLLM_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": allowed,
        "max_completion_tokens": allowed,
        "temperature": 0.1,
        "stream": False,
        "n": 1,
    }

async def call_llm(req: dict) -> str:
    vllm_chat_url = settings.VLLM_URL.rstrip("/") + "/chat/completions"
    async with httpx.AsyncClient(timeout=httpx.Timeout(75.0)) as client:
        resp = await client.post(vllm_chat_url, json=req)
        resp.raise_for_status()
        data = resp.json()
    return (data.get("choices", [{}])[0].get("message", {}).get("content") or "").strip()
