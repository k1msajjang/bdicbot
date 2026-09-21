from pydantic import BaseModel, Field

class CreateKnowledgeBaseRequest(BaseModel):
    judul: str = Field(..., min_length=1, max_length=150)
    jawaban: str = Field(..., min_length=1)
    category_ids: list[int] = Field(..., min_length=1)
    program_ids: list[int] = Field(..., min_length=1)
    tag_ids: list[int] = Field(default_factory=list)

class ToggleStatusRequest(BaseModel):
    status: bool

class UpdateKnowledgeBaseRequest(CreateKnowledgeBaseRequest):
    pass