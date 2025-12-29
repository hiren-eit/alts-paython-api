from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class AddFileCommentRequest(BaseModel):
    fileuid: UUID
    comment: str
    createdby: Optional[str] = "System"
