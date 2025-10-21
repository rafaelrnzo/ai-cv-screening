import os
from typing import List
from app.core.config import settings

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.GROUND_DIR, exist_ok=True)

def save_upload_bytes(filename: str, data: bytes) -> str:
    import uuid
    fid = str(uuid.uuid4())
    _, ext = os.path.splitext(filename or "")
    ext = ext.lower() or ".txt"
    path = os.path.join(settings.UPLOAD_DIR, f"{fid}{ext}")
    with open(path, "wb") as o:
        o.write(data)
    return fid

def path_by_id(fid: str) -> str:
    for n in os.listdir(settings.UPLOAD_DIR):
        if n.startswith(fid):
            return os.path.join(settings.UPLOAD_DIR, n)
    raise FileNotFoundError(fid)

def read_file_text(path: str) -> str:
    lower = path.lower()
    if lower.endswith(".pdf"):
        return f"(PDF file at {os.path.basename(path)} — add PDF text extraction in production)"
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        with open(path, "rb") as f:
            data = f.read(2048)
        return f"(Binary file {os.path.basename(path)}; first 2KB) " + repr(data[:200])

def join_ctx(rows: List[dict]) -> str:
    return "\n\n".join(f"[{x['doc_type']}] {x['title']}: {x['text']}" for x in rows)
