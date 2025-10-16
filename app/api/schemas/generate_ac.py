from pydantic import BaseModel

class GenerateACRequest(BaseModel):
    template_format: str = ""
    context_acceptance_criteria: str = "" 