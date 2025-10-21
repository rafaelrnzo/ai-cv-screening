from fastapi import FastAPI, APIRouter
from app.api.v1.endpoints import health, evaluate

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(evaluate.router)