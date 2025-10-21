import os
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from app.api.schemas.schemas import EvaluateRequest
from app.services.pipeline_service import create_job, run_pipeline, get_job
from app.utils.file_io import save_upload_bytes, path_by_id

router = APIRouter(prefix="/evaluate", tags=["Evaluate"])

@router.post("/upload")
async def upload(cv: UploadFile = File(...), report: UploadFile = File(...)):
    try:
        cv_bytes = await cv.read()
        report_bytes = await report.read()
        cv_id = save_upload_bytes(cv.filename, cv_bytes)
        report_id = save_upload_bytes(report.filename, report_bytes)
        return {"cv_id": cv_id, "report_id": report_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Upload failed: {e}")

@router.post("")
def evaluate(req: EvaluateRequest, bg: BackgroundTasks):
    # fail fast if not found
    _ = path_by_id(req.cv_id)
    _ = path_by_id(req.report_id)

    job_id = create_job()
    bg.add_task(run_pipeline, job_id, req.job_title, req.cv_id, req.report_id)
    return {"id": job_id, "status": "queued"}

@router.get("/result/{job_id}")
def result(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    if job["status"] in ("queued", "processing"):
        return {"id": job_id, "status": job["status"]}
    if job["status"] == "completed":
        return {"id": job_id, "status": "completed", "result": job["result"]}
    return {"id": job_id, "status": "failed", "error": job.get("error", "unknown")}
