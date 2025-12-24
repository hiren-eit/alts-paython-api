from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class AddDocumentCommentRequest(BaseModel):
    fileuid: UUID
    comment: str
    createdby: Optional[str] = "System"
