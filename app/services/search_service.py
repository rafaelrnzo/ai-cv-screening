from typing import List, Optional, Dict, Any
from app.core.redis_client import knn_search, ensure_index_and_seed
from app.utils.file_io import join_ctx

def search_ctx(query: str, k: int, types: Optional[List[str]] = None) -> str:
    ensure_index_and_seed()
    rows = knn_search(query, k=k, types=types)
    return join_ctx(rows)

def get_contexts_for_pipeline(job_title: str) -> Dict[str, str]:
    return {
        "jd_ctx":         search_ctx(job_title, k=3, types=["job_description"]),
        "cv_rubric_ctx":  search_ctx("cv rubric", k=2, types=["cv_rubric"]),
        "brief_ctx":      search_ctx("case study brief", k=2, types=["case_brief"]),
        "proj_rubric_ctx":search_ctx("project rubric", k=2, types=["project_rubric"]),
    }
