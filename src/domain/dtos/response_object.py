from pydantic import BaseModel, Field
from typing import Any, Optional


class ResponseObject(BaseModel):
    result_code: Optional[str] = Field(
        None, description="Application-specific result code", example="200"
    )
    count: int = Field(
        0, description="Total number of records returned in the response", example=5
    )
    result_object: Optional[Any] = Field(None, description="Actual response payload")
    result_message: Optional[str] = Field(None, description="Human-readable message")
