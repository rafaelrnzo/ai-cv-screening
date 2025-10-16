from fastapi import HTTPException
from app.core.config import settings
from app.core.llm_client import build_llm_request, call_llm
from app.core.redis_client import search_similar_context

def clip_text(s: str, n: int) -> str:
    return (s or "")[:n]

async def generate_acceptance_criteria(template_format: str, context_acceptance_criteria: str):
    system_prompt = "Kamu adalah asisten AI untuk membantu penulisan Acceptance Criteria yang baik."

    try:
        retrieved = search_similar_context(context_acceptance_criteria, top_k=3)
    except Exception:
        retrieved = []

    bullets = ""
    if retrieved:
        refs = [f"- {d['user_stories']}" for d in retrieved if d.get("user_stories")]
        if refs:
            bullets = "\n\n--\nReferensi serupa:\n" + "\n".join(refs)

    user_prompt = (
        "Gunakan format berikut sebagai panduan untuk menuliskan Acceptance Criteria:\n\n"
        f"{clip_text(template_format, settings.MAX_CHARS_TEMPLATE)}\n\n"
        "Berikut adalah konteks/konten Acceptance Criteria yang relevan (gunakan sebagai referensi saja):\n\n"
        f"{clip_text(context_acceptance_criteria, settings.MAX_CHARS_CONTEXT)}"
        f"{bullets}\n\n"
        "Tulis hasil akhir dalam format markdown yang rapi (tanpa blok kode ```), "
        "tanpa penjelasan tambahan, dan sesuai standar Agile (Given/When/Then atau poin terstruktur)."
    )

    req = build_llm_request(system_prompt, user_prompt)
    content = await call_llm(req)

    if not content:
        raise HTTPException(status_code=500, detail="Empty content from LLM")

    return {"status": "success", "model": settings.VLLM_MODEL, "response": content}
