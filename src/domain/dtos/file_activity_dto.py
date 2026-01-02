from pydantic import BaseModel, Field
from typing import List, Optional, Any,Dict
from uuid import UUID
from datetime import date

class FileActivityResponse(BaseModel):
    fileuid: Optional[UUID] = None
    status: Optional[str] = None
    stage: Optional[str] = None
    file_processing_stage: Optional[str] = None
    failure_stage: Optional[str] = None
    status_comment: Optional[str] = None
    comment: Optional[str] = None
    is_commented: Optional[bool] = False
    file_details: Optional[Dict] = None
    created: Any = None
    createdby: Optional[str] = None
    updated: Optional[Any] = None
    updatedby: Optional[str] = None
    is_active: bool = True
    

