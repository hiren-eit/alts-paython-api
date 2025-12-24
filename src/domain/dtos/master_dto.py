from datetime import datetime
from typing import Optional, Any
from uuid import UUID
from pydantic import BaseModel, Field

class ResponseObjectModel(BaseModel):
    """
        Master Response Model - Can return any kind of data as a response
    """
    result_code: Optional[str] = Field(default=None, description="Result code from the server")
    total: int = Field(default=0, description="Total data objects in response")
    data: Any = Field(default=None, description="Data got from the server")
    result_message: Optional[str] = Field(default=None, description="Result message from the server")

    class Config:
        json_schema_extra = {
            "example": {
                "result_code": "Success",
                "total": 0,
                "data": None,
                "message": "Response Message"
            }
        }


class Document(BaseModel):
    id: int = Field(description="File ID")
    created: datetime = Field(default_factory=datetime.utcnow, description="Created UTC time")
    created_by: Optional[str] = Field(default="SYSTEM", max_length=255, description="Creator")
    updated: Optional[datetime] = Field(default=None, description="Last updated time")
    updated_by: Optional[str] = Field(default=None, max_length=255, description="Last updater")
    is_active: bool = Field(default=True, description="Active flag")

    # Core document identifiers
    doc_uid: UUID = Field(description="DocUID")
    # counter: Optional[int] = Field(default=None, description="Counter")
    type: Optional[str] = Field(default=None, description="Document type")
    filename: Optional[str] = Field(default=None, description="File name")
    firm: Optional[int] = Field(default=None, description="Firm id")
    entity_uid: Optional[UUID] = Field(default=None, description="Entity UID")
    account_sid: Optional[str] = Field(default=None, description="Account SID")
    account_uid: Optional[UUID] = Field(default=None, description="Account UID")
    position_uid: Optional[UUID] = Field(default=None, description="Position UID")

    # NotMapped fields (in C#)
    content: Optional[str] = Field(default=None, description="Document content")
    document_name: Optional[str] = Field(default=None, description="Document name")
    source: Optional[str] = Field(default=None, description="Source")
    file_type: Optional[str] = Field(default=None, description="File type")
    processing_method: Optional[str] = Field(default=None, description="Processing method")

    # Persistence-related fields
    file_path: Optional[str] = Field(default=None, description="File path")
    report_date: Optional[str] = Field(default=None, description="Report date")
    create_date: Optional[datetime] = Field(default=None, description="Create date")
    create_time: Optional[datetime] = Field(default=None, description="Create time")
    module: Optional[str] = Field(default=None, description="Module")
    work_sid: Optional[str] = Field(default=None, description="Work SID")
    work_uid: Optional[UUID] = Field(default=None, description="Work UID")
    comments: Optional[str] = Field(default=None, description="Comments")
    tag: Optional[str] = Field(default=None, description="Tag")
    create_by: Optional[str] = Field(default=None, description="Created by (domain field)")
    # client_entity_uid: Optional[UUID] = Field(default=None, description="Client entity UID")
    filename_alt: Optional[str] = Field(default=None, description="Alternate file name")
    # external_id: Optional[str] = Field(default=None, description="External ID")
    batch_id: Optional[str] = Field(default=None, description="Batch ID")
    pub_uid: Optional[UUID] = Field(default=None, description="Publication UID")
    metadata: Optional[str] = Field(default=None, description="Metadata")
    checksum: Optional[str] = Field(default=None, description="Checksum")
    status: Optional[str] = Field(default=None, description="Status")
    status_date: Optional[datetime] = Field(default=None, description="Status date")
    method: Optional[str] = Field(default=None, description="Method")
    # doc_sid: Optional[str] = Field(default=None, description="Document SID")
    link_uid: Optional[UUID] = Field(default=None, description="Link UID")
    # available_date: Optional[datetime] = Field(default=None, description="Available date")
    notice_date: Optional[datetime] = Field(default=None, description="Notice date")
    reason_id: Optional[str] = Field(default=None, description="Reason ID")
    reason: Optional[str] = Field(default=None, description="Reason")
    harvest_system: Optional[str] = Field(default=None, description="Harvest system")
    harvest_method: Optional[str] = Field(default=None, description="Harvest method")
    harvest_source: Optional[str] = Field(default=None, description="Harvest source")
    index_system: Optional[str] = Field(default=None, description="Index system")
    index_method: Optional[str] = Field(default=None, description="Index method")
    extract_system: Optional[str] = Field(default=None, description="Extract system")
    extract_method: Optional[str] = Field(default=None, description="Extract method")
    age: Optional[int] = Field(default=None, description="Age")
    email_sender: Optional[str] = Field(default=None, description="Email sender")
    email_subject: Optional[str] = Field(default=None, description="Email subject")
    category: Optional[str] = Field(default=None, description="Category")
    failure_stage: Optional[str] = Field(default=None, description="Failure stage")
    document_type_procees_rule: Optional[str] = Field(default=None, description="Document type process rule")
    document_type_gen_ai: Optional[str] = Field(default=None, description="Document type GenAI")
    ignored_on: Optional[datetime] = Field(default=None, description="Ignored on")
    ignored_by: Optional[str] = Field(default=None, description="Ignored by")
    rule: Optional[str] = Field(default=None, description="Rule")
    business_date: Optional[datetime] = Field(default=None, description="Business date")
    firm_name: Optional[str] = Field(default=None, description="Firm name")
    entity_name: Optional[str] = Field(default=None, description="Entity name")
    account_name: Optional[str] = Field(default=None, description="Account name")
    capture_method: Optional[str] = Field(default=None, description="Capture method")
    # capture_system: Optional[str] = Field(default=None, description="Capture system")
    linking_method: Optional[str] = Field(default=None, description="Linking method")
    linking_system: Optional[str] = Field(default=None, description="Linking system")
    source_attributes: Optional[str] = Field(default=None, description="Source attributes")
    investor: Optional[str] = Field(default=None, description="Investor")

    # Stage / workflow
    stage: Optional[str] = Field(default=None, description="Stage")  # or Enum if you port DocumentProcessStage
    duplicate_document_id: Optional[UUID] = Field(default=None, description="Duplicate document ID")
    update_document_id: Optional[UUID] = Field(default=None, description="Update document ID")
    status_comment: Optional[str] = Field(default=None, description="Status comment")
    document_process_stage: Optional[str] = Field(default=None, description="Document process stage")
    business_rule_applied_date: Optional[datetime] = Field(default=None, description="Business rule applied date")

    # File metadata / security
    file_extension: Optional[str] = Field(default=None, description="File extension")
    password: Optional[str] = Field(default=None, description="Password")
    group_code: Optional[str] = Field(default=None, description="Group code")
    replay: Optional[bool] = Field(default=None, description="Replay flag")
    last_attempted_time: Optional[datetime] = Field(default=None, description="Last attempted time")
    retry_count: Optional[int] = Field(default=None, description="Retry count")
    ingestion_failed_image_url: Optional[str] = Field(default=None, description="Ingestion failed image URL")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "created": "2025-12-17T10:24:29.095Z",
                "created_by": "string",
                "updated": "2025-12-17T10:24:29.095Z",
                "updated_by": "string",
                "is_active": True,
                "doc_uid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                # "counter": 0,
                "type": "string",
                "filename": "string",
                "firm": 0,
                "entity_uid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "account_sid": "string",
                "account_uid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "position_uid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "content": "string",
                "document_name": "string",
                "source": "string",
                "file_type": "string",
                "processing_method": "string",
                "file_path": "string",
                "report_date": "string",
                "create_date": "2025-12-17T10:24:29.095Z",
                "create_time": "2025-12-17T10:24:29.095Z",
                "module": "string",
                "work_sid": "string",
                "work_uid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "comments": "string",
                "tag": "string",
                "create_by": "string",
                # "client_entity_uid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "filename_alt": "string",
                # "external_id": "string",
                "batch_id": "string",
                "pub_uid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "metadata": "string",
                "checksum": "string",
                "status": "string",
                "status_date": "2025-12-17T10:24:29.095Z",
                "method": "string",
                # "doc_sid": "string",
                "link_uid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                # "available_date": "2025-12-17T10:24:29.095Z",
                "notice_date": "2025-12-17T10:24:29.095Z",
                "reason_id": "string",
                "reason": "string",
                "harvest_system": "string",
                "harvest_method": "string",
                "harvest_source": "string",
                "index_system": "string",
                "index_method": "string",
                "extract_system": "string",
                "extract_method": "string",
                "age": 0,
                "email_sender": "string",
                "email_subject": "string",
                "category": "string",
                "failure_stage": "string",
                "document_type_procees_rule": "string",
                "document_type_gen_ai": "string",
                "ignored_on": "2025-12-17T10:24:29.095Z",
                "ignored_by": "string",
                "rule": "string",
                "business_date": "2025-12-17T10:24:29.095Z",
                "firm_name": "string",
                "entity_name": "string",
                "capture_method": "string",
                # "capture_system": "string",
                "linking_method": "string",
                "linking_system": "string",
                "source_attributes": "string",
                "investor": "string",
                "stage": "DocReady",
                "duplicate_document_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "update_document_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "status_comment": "string",
                "document_process_stage": "string",
                "business_rule_applied_date": "2025-12-17T10:24:29.095Z",
                "file_extension": "string",
                "password": "string",
                "group_code": "string",
                "replay": True,
                "last_attempted_time": "2025-12-17T10:24:29.095Z",
                "retry_count": 0,
                "ingestion_failed_image_url": "string",
            }
        }

class ResolveUpdateInputModel(BaseModel):
    selected_doc_uid: UUID = Field(description="Selected Document UUID")
    ignored_doc_uid: UUID = Field(description="Ignored Document UUID")
    is_update_selected: bool = Field(description="Indicate if selected document is updated or not")
    updated_by: Optional[str] = Field(default=None, description="Name of the user who updated")

    class Config:
        json_schema_extra = {
            "example": {
                "selected_doc_uid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "ignored_doc_uid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "is_update_selected": True,
                "updated_by": "string"
            }
        }