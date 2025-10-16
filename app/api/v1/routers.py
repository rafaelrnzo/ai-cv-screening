from fastapi import FastAPI, APIRouter
from app.api.v1.endpoints import health, generate_acceptance_criteria, generate_subtask

api_router = APIRouter()

api_router.include_router(generate_acceptance_criteria.router) 
api_router.include_router(generate_subtask.router) 
api_router.include_router(health.router) 