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


@router.post("", summary="Create evaluation job")
def evaluate(req: EvaluateRequest, bg: BackgroundTasks):
    try:
        _ = path_by_id(req.cv_id)
        _ = path_by_id(req.report_id)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    job_id = create_job(req.job_title, req.cv_id, req.report_id)
    bg.add_task(run_pipeline, job_id, req.job_title, req.cv_id, req.report_id)
    return {"id": job_id, "status": "queued"}


@router.get("/result/{job_id}", summary="Get job status/result")
def result(job_id: str):
    resp = get_job(job_id)
    if not resp:
        raise HTTPException(status_code=404, detail="job not found")
    return resp
