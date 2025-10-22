import json
import google.generativeai as genai
from app.core.config import settings

genai.configure(api_key=settings.GOOGLE_API_KEY)

def gen_json(prompt: str) -> dict:
    model = genai.GenerativeModel(settings.GEMINI_MODEL)
    out = model.generate_content(prompt)
    txt = (out.text or "").strip()
    try:
        return json.loads(txt)
    except Exception:
        s, e = txt.find("{"), txt.rfind("}")
        if s != -1 and e != -1 and e > s:
            try:
                return json.loads(txt[s:e+1])
            except Exception:
                pass
        return {"_raw": txt[:300]}
