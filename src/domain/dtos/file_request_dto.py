from typing import List, Optional
from pydantic import BaseModel, Field


class Content(BaseModel):
    filename: str = Field(..., description="Name of the uploaded file")
    file: str = Field(..., description="Base64-encoded file content")


class FileRequestDTO(BaseModel):
    type: str = Field(..., description="File type identifier")
    harvest_source: str = Field(
        ..., description="Source system from which the file is harvested"
    )
    files: List[Content] = Field(
        ..., description="List of files associated with the request"
    )
    haas: bool = Field(
        ..., description="Indicates whether the request is processed in HAAS mode"
    )
    created_by: Optional[str] = Field(
        None, description="User or system that created the request"
    )
