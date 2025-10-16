# app/routers/subtask.py
import re
import json
import requests
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.config import settings
from app.api.schemas.generate_subtask import GenerateRequest, GenerateResponse

AI_API_BASE = settings.VLLM_URL
AI_MODEL    = settings.VLLM_MODEL
AI_TIMEOUT  = 60  

SYSTEM_PROMPT = (
    "Anda adalah AI Project Assistant. "
    "Berdasarkan acceptance criteria berikut, buatkan daftar subtask yang relevan. "
    "Balas hanya dalam format JSON array, tanpa penjelasan tambahan.\n\n"
    "Contoh format:\n"
    "[\"Membuat model database task\", \"Membangun API endpoint\", \"Mendesain UI\"]"
)

router = APIRouter(prefix=f"/generate-subtask", tags=["Subtask"])


def _extract_json_array(text: str) -> list:
    if not text:
        return []
    match = re.search(r'\[.*\]', text, re.DOTALL)
    json_text = match.group(0) if match else text.strip()
    json_text = re.sub(r'^```(?:json)?\s*', '', json_text.strip())
    json_text = re.sub(r'\s*```$', '', json_text.strip())
    try:
        return json.loads(json_text)
    except json.JSONDecodeError:
        try:
            return json.loads(json_text.replace("'", '"'))
        except Exception:
            return []

def _clean_title(title: str) -> str:
    if not isinstance(title, str):
        return ""
    return re.sub(r'[-*•\n\r\t]+', ' ', title).strip()

def _resolve_model(in_model: Optional[str]) -> str:
    cand = (in_model or "").strip()
    if cand.lower() in {"", "string", "none", "null"}:
        return AI_MODEL
    return cand

def _post_chat(payload: dict) -> requests.Response:
    url = f"{AI_API_BASE.rstrip('/')}/chat/completions"
    return requests.post(url, json=payload, timeout=AI_TIMEOUT)

@router.post("/generate-subtasks", response_model=GenerateResponse)
def generate_subtasks(req: GenerateRequest):
    if not req.acceptance_criteria or not req.acceptance_criteria.strip():
        raise HTTPException(status_code=400, detail="acceptance_criteria is required")

    model = _resolve_model(req.model)

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": req.acceptance_criteria},
        ],
        "temperature": req.temperature or 0.7,
    }

    try:
        r = _post_chat(payload)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM upstream error: {e}")

    if r.status_code == 404 and model != AI_MODEL:
        try:
            r = _post_chat({**payload, "model": AI_MODEL})
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"LLM upstream error (fallback): {e}")

    if not r.ok:
        body = r.text
        if len(body) > 1200:
            body = body[:1200] + "...(truncated)"
        raise HTTPException(
            status_code=502,
            detail=f"LLM upstream bad status: {r.status_code} - {body}"
        )

    result = r.json()
    try:
        content = result["choices"][0]["message"]["content"]
    except Exception:
        raise HTTPException(status_code=502, detail="Invalid LLM response schema")

    subtasks = _extract_json_array(content)
    if not isinstance(subtasks, list) or not subtasks:
        raise HTTPException(status_code=422, detail="LLM output is not a valid JSON array")

    cleaned, seen = [], set()
    for t in subtasks:
        ct = _clean_title(t)
        if ct and ct.lower() not in seen:
            cleaned.append(ct)
            seen.add(ct.lower())

    if not cleaned:
        raise HTTPException(status_code=422, detail="No valid subtask titles after cleaning")

    return GenerateResponse(subtasks=cleaned)
