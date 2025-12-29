from pydantic import BaseModel
from typing import Optional, Any
from uuid import UUID

class ResponseObjectModel(BaseModel):
    resultcode: str
    resultobject: Optional[Any] = None
    resultmessage: str

class ExtractionFileDetailModel(BaseModel):
    fileuid: UUID
    extracteddata: Optional[str] = None
    classification: Optional[str] = None

class UpdateExtractFileRequest(BaseModel):
    extraction_document_detail: ExtractionFileDetailModel
    updatedby: Optional[str] = "SYSTEM"
    old_audit_json: Optional[str] = None
    audit_updated_json: Optional[str] = None
