import os
import uuid
from pathlib import Path
from app.core.config import settings

def _ensure_upload_dir() -> str:
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    return settings.UPLOAD_DIR

def save_upload_bytes(filename: str, data: bytes) -> str:
    _ensure_upload_dir()
    fid = str(uuid.uuid4())
    _, ext = os.path.splitext(filename or "")
    ext = ext or ".txt"
    path = os.path.join(settings.UPLOAD_DIR, f"{fid}{ext}")
    with open(path, "wb") as f:
        f.write(data)
    return fid

def path_by_id(fid: str) -> str:
    base = _ensure_upload_dir()
    for name in os.listdir(base):
        if name.startswith(fid):
            return os.path.join(base, name)
    raise FileNotFoundError(f"file id not found: {fid}")

def read_file_text(path: str) -> str:
    lower = path.lower()
    if lower.endswith(".pdf"):
        try:
            from pypdf import PdfReader
            reader = PdfReader(path)
            pages = [p.extract_text() or "" for p in reader.pages]
            text = "\n".join(pages).strip()
            return text if text else "(empty pdf text)"
        except Exception as e:
            return f"(pdf parse error: {e})"
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        with open(path, "rb") as f:
            data = f.read(2048)
        return f"(binary file {os.path.basename(path)}; first 2KB) {repr(data[:200])}"

def join_ctx(rows: list[dict]) -> str:
    if not rows:
        return ""
    return "\n\n".join(f"[{row.get('doc_type')}] {row.get('title')}: {row.get('text')}" for row in rows)
