"""
TLDR: Pydantic schemas for API payloads.
Logic: Validates incoming request data structure and explicitly formats outgoing responses 
to maintain strict REST protocol constraints.
"""
from pydantic import BaseModel, Field
from typing import Optional

class QueryRequest(BaseModel):
    query: str = Field(..., example="A person doing a pushup")
    top_k: int = Field(default=1, ge=1)
    threshold: float = Field(default=1.40, example=1.30)

class SceneInfo(BaseModel):
    scene_idx: int
    start_time: float
    end_time: float

class QueryResult(BaseModel):
    score: float
    scene: SceneInfo
    video_url: Optional[str] = None

if __name__ == "__main__":
    req = QueryRequest(query="Test", top_k=3)
    print(f"Validated Request Schema: {req.dict()}")