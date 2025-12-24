"""
Document Receiver DTOs - Request/Response models for DocumentService and DocumentReceiver APIs
Mirrors all parameters and response fields.
"""

from typing import List
from pydantic import BaseModel, Field

class DocumentRequestModel(BaseModel):
    type: str = Field(description="Type of the document")
    harvest_source: str = Field(description="Harvest source of the documentation")
    documents: List[Content] = Field(description="Uploaded file's content and name")
    haas: bool = Field(description="Will be true if Harvest Only is selected while uploading file")
    created_by: str = Field(description="Name of the use who uploads the file")

    class Config:
        json_schema_extra = {
            "example": {
                "type": "string",
                "harvest_source": "string",
                "documents": [
                    {
                    "file_name": "string",
                    "document": "string"
                    }
                ],
                "haas": True,
                "created_by": "string"
            }
        }


class Content(BaseModel):
    file_name: str = Field(description="Name of the uploaded file")
    document: str = Field(description="Content of the file encoded into string")
