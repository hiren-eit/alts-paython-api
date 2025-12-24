from pydantic import BaseModel
from typing import Optional, Any
from uuid import UUID

class ResponseObjectModel(BaseModel):
    resultcode: str
    resultobject: Optional[Any] = None
    resultmessage: str

class ExtractionDocumentDetailModel(BaseModel):
    fileuid: UUID
    extracteddata: Optional[str] = None
    classification: Optional[str] = None

class UpdateExtractDocumentRequest(BaseModel):
    extraction_document_detail: ExtractionDocumentDetailModel
    updatedby: Optional[str] = "SYSTEM"
    old_audit_json: Optional[str] = None
    audit_updated_json: Optional[str] = None
