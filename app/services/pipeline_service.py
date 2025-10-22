import json
import uuid
from typing import Dict, Any

from app.core.llm_client import gen_json
from app.services.search_service import get_contexts_for_pipeline
from app.utils.file_io import path_by_id, read_file_text

from app.db.session import SessionLocal
from app.db.models import JobResult

def prompt_cv(cv_text: str, jd_ctx: str, rubric_ctx: str) -> str:
    return f"""
You are an expert technical recruiter. Evaluate the following CV against the job description and the scoring rubric.

CV:
{cv_text[:3000]}

Job Description Context:
{jd_ctx}

CV Scoring Rubric:
{rubric_ctx}

Return STRICT JSON:
{{
  "cv_match_rate": <float 0..1>,
  "cv_feedback": "<<=120 words concise feedback>"
}}
"""

def prompt_proj(report_text: str, brief_ctx: str, rubric_ctx: str) -> str:
    return f"""
You are a senior backend/AI reviewer. Evaluate the candidate's project report against the case brief and the project rubric.

Project Report:
{report_text[:3000]}

Case Study Brief Context:
{brief_ctx}

Project Scoring Rubric:
{rubric_ctx}

Return STRICT JSON:
{{
  "project_score": <number 1..5 allow .5>,
  "project_feedback": "<<=120 words concise feedback>"
}}
"""

def prompt_final(cvj: dict, projj: dict) -> str:
    return f"""
You are writing a concise hiring panel note. Based on the two JSON blobs:

CV_EVAL = {json.dumps(cvj, ensure_ascii=False)}
PROJECT_EVAL = {json.dumps(projj, ensure_ascii=False)}

Write a 3–5 sentence 'overall_summary' that states strengths, gaps, and a clear recommendation.

Return STRICT JSON:
{{
  "overall_summary": "<3-5 sentences>"
}}
"""

def _update_job(job_id: str, **fields) -> None:
    db = SessionLocal()
    try:
        row = db.query(JobResult).filter(JobResult.id == job_id).first()
        if not row:
            return
        for k, v in fields.items():
            setattr(row, k, v)
        db.commit()
    finally:
        db.close()

def _to_response(row: JobResult) -> Dict[str, Any]:
    if not row:
        return {}
    if row.status in ("queued", "processing"):
        return {"id": row.id, "status": row.status}
    if row.status == "completed":
        return {
            "id": row.id,
            "status": "completed",
            "result": {
                "cv_match_rate": row.cv_match_rate,
                "cv_feedback": row.cv_feedback,
                "project_score": row.project_score,
                "project_feedback": row.project_feedback,
                "overall_summary": row.overall_summary,
            },
        }
    return {"id": row.id, "status": "failed", "error": row.error or "unknown"}

def _require_nonempty(name: str, value: str, min_len: int = 20):
    if not value or len(value.strip()) < min_len:
        raise ValueError(f"{name} is empty/too short")

def create_job(job_title: str, cv_id: str, report_id: str) -> str:
    job_id = str(uuid.uuid4())
    db = SessionLocal()
    try:
        row = JobResult(
            id=job_id,
            job_title=job_title,
            cv_id=cv_id,
            report_id=report_id,
            status="queued",
        )
        db.add(row)
        db.commit()
    finally:
        db.close()
    return job_id

def run_pipeline(job_id: str, job_title: str, cv_id: str, report_id: str) -> None:
    _update_job(job_id, status="processing")

    try:
        cv_path = path_by_id(cv_id)
        report_path = path_by_id(report_id)
        cv_text = read_file_text(cv_path)
        report_text = read_file_text(report_path)

        ctx = get_contexts_for_pipeline(job_title)
        jd_ctx = ctx.get("jd_ctx", "")
        cv_rb = ctx.get("cv_rubric_ctx", "")
        brief = ctx.get("brief_ctx", "")
        pr_rb = ctx.get("proj_rubric_ctx", "")

        _require_nonempty("CV text", cv_text)
        _require_nonempty("Job Description context", jd_ctx)
        _require_nonempty("CV Rubric context", cv_rb)
        _require_nonempty("Project Report text", report_text)
        _require_nonempty("Case Brief context", brief)
        _require_nonempty("Project Rubric context", pr_rb)

        cv_json = gen_json(prompt_cv(cv_text, jd_ctx, cv_rb))
        proj_json = gen_json(prompt_proj(report_text, brief, pr_rb))
        final_json = gen_json(prompt_final(cv_json, proj_json))

        _update_job(
            job_id,
            status="completed",
            cv_match_rate=cv_json.get("cv_match_rate"),
            cv_feedback=cv_json.get("cv_feedback"),
            project_score=proj_json.get("project_score"),
            project_feedback=proj_json.get("project_feedback"),
            overall_summary=final_json.get("overall_summary"),
            error=None,
        )

    except Exception as e:
        _update_job(job_id, status="failed", error=str(e))


def get_job(job_id: str) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        row = db.query(JobResult).filter(JobResult.id == job_id).first()
    finally:
        db.close()
    return _to_response(row)
