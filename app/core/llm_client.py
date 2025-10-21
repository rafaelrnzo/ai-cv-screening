import json
import google.generativeai as genai
from app.core.config import settings

if not settings.GOOGLE_API_KEY:
    raise RuntimeError("Please set GOOGLE_API_KEY in environment (.env)")
genai.configure(api_key=settings.GOOGLE_API_KEY)

def gen_json(prompt: str) -> dict:
    model = genai.GenerativeModel(settings.GEMINI_MODEL)
    out = model.generate_content(prompt)
    txt = (out.text or "").strip()

    try:
        return json.loads(txt)
    except Exception:
        start = txt.find("{")
        end = txt.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(txt[start:end+1])
            except Exception:
                pass
        # Fallback for debugging
        return {"_raw": txt[:300]}
