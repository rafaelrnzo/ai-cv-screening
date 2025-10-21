import json
import time
import uuid
from typing import Dict, Any

from app.core.llm_client import gen_json
from app.services.search_service import get_contexts_for_pipeline
from app.utils.file_io import path_by_id, read_file_text

JOBS: Dict[str, Dict[str, Any]] = {}

# ---------- Prompts ----------
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

# ---------- Orchestrator ----------
def create_job() -> str:
    job_id = str(uuid.uuid4())
    JOBS[job_id] = {"status": "queued", "result": None, "created_at": time.time()}
    return job_id

def run_pipeline(job_id: str, job_title: str, cv_id: str, report_id: str) -> None:
    try:
        JOBS[job_id]["status"] = "processing"

        cv_path = path_by_id(cv_id)
        report_path = path_by_id(report_id)
        cv_text = read_file_text(cv_path)
        report_text = read_file_text(report_path)

        ctx = get_contexts_for_pipeline(job_title)

        cv_json = gen_json(prompt_cv(cv_text, ctx["jd_ctx"], ctx["cv_rubric_ctx"]))
        proj_json = gen_json(prompt_proj(report_text, ctx["brief_ctx"], ctx["proj_rubric_ctx"]))
        final_json = gen_json(prompt_final(cv_json, proj_json))

        JOBS[job_id]["status"] = "completed"
        JOBS[job_id]["result"] = {
            "cv_match_rate": cv_json.get("cv_match_rate"),
            "cv_feedback": cv_json.get("cv_feedback"),
            "project_score": proj_json.get("project_score"),
            "project_feedback": proj_json.get("project_feedback"),
            "overall_summary": final_json.get("overall_summary"),
        }
    except Exception as e:
        JOBS[job_id]["status"] = "failed"
        JOBS[job_id]["error"] = str(e)

def get_job(job_id: str) -> Dict[str, Any]:
    return JOBS.get(job_id, {})
