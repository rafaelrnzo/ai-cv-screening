from typing import List, Optional
from pydantic import BaseModel

class GenerateRequest(BaseModel):
    acceptance_criteria: str
    temperature: Optional[float] = 0.7
    model: Optional[str] = None

class GenerateResponse(BaseModel):
    subtasks: List[str]