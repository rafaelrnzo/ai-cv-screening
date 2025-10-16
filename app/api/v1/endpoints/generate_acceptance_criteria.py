from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.api.schemas.generate_ac import GenerateACRequest
from app.services.acceptance_service import generate_acceptance_criteria

router = APIRouter(prefix="/acceptance-criteria", tags=["Acceptance Criteria"])

@router.post("/generate")
async def generate_ac(payload: GenerateACRequest, request: Request):
    result = await generate_acceptance_criteria(
        payload.template_format, payload.context_acceptance_criteria
    )
    return JSONResponse(content=result)
