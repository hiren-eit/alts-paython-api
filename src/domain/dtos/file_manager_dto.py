"""
Document Manager DTOs - Request/Response models for GetDocumentManager API
Mirrors all parameters and response fields from the SQL Server stored procedure.
"""
from datetime import date, datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class FileManagerFilter(BaseModel):
    """
    Request filter model - matches all SP parameters:
    @DocType, @DocumentStatus, @FilterJson, @PageNumber, @PageSize,
    @SortColumn, @SortOrder, @Visibility, @SlaType
    """
    # Core SP parameters
    doc_type: str = Field(default="All", description="Document type filter")
    document_status: str = Field(default="ToReview", description="Tab/status filter: All, ToReview, Approved, captured, extracted, linked, ingested, duplicates, completed, INPROGRESS, IGNORED")
    page_number: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(default=100, ge=1, le=1000, description="Results per page")
    sort_column: Optional[str] = Field(default=None, description="Column to sort by")
    sort_order: Optional[str] = Field(default="desc", description="Sort order: asc or desc")
    visibility: str = Field(default="S", description="Visibility mode: S for tokenized, else normal")
    sla_type: str = Field(default="All", description="SLA filter: All, withinsla, onsla, slabreached, uncategorized")
    
    # FilterJson fields - parsed from JSON in SP
    search_text: Optional[List[str]] = Field(default=None, description="Search text(s) for filename, docuid, emailsubject, etc.")
    firm_ids: Optional[List[int]] = Field(default=None, description="Firm ID filter")
    entity_ids: Optional[List[str]] = Field(default=None, description="Entity UID filter")
    file_types: Optional[List[str]] = Field(default=None, description="File extension filter")
    document_type_gen_ai: Optional[List[str]] = Field(default=None, description="GenAI document type filter")
    document_type_procees_rule: Optional[List[str]] = Field(default=None, description="Process rule document type filter")
    doc_uids: Optional[List[str]] = Field(default=None, description="Document UID filter")
    status_comments: Optional[List[str]] = Field(default=None, description="Status comment filter")
    failure_stages: Optional[List[str]] = Field(default=None, description="Failure stage filter")
    reasons: Optional[List[str]] = Field(default=None, description="Reason filter")
    last_stages: Optional[List[str]] = Field(default=None, description="Last stage filter")
    processing_methods: Optional[List[str]] = Field(default=None, description="Processing method filter")
    capture_methods: Optional[List[str]] = Field(default=None, description="Capture method filter")
    capture_systems: Optional[List[str]] = Field(default=None, description="Capture system filter")
    extract_methods: Optional[List[str]] = Field(default=None, description="Extract method filter")
    extract_systems: Optional[List[str]] = Field(default=None, description="Extract system filter")
    senders: Optional[List[str]] = Field(default=None, description="Email sender filter")
    subjects: Optional[List[str]] = Field(default=None, description="Email subject filter")
    ignored_by: Optional[List[str]] = Field(default=None, description="Ignored by user filter")
    account_sids: Optional[List[str]] = Field(default=None, description="Account SID filter")
    account_uids: Optional[List[str]] = Field(default=None, description="Account UID filter")
    
    # Date range filters
    filter_created_date_from: Optional[date] = Field(default=None, description="Created date from")
    filter_created_date_to: Optional[date] = Field(default=None, description="Created date to")
    filter_status_date_from: Optional[date] = Field(default=None, description="Status date from")
    filter_status_date_to: Optional[date] = Field(default=None, description="Status date to")
    filter_business_date_from: Optional[date] = Field(default=None, description="Business date from")
    filter_business_date_to: Optional[date] = Field(default=None, description="Business date to")
    
    # Single value filters
    source: Optional[str] = Field(default=None, description="Harvest source filter")
    linking_method: Optional[str] = Field(default=None, description="Linking method filter")
    batch_id: Optional[str] = Field(default=None, description="Batch ID filter")
    
    class Config:
        json_schema_extra = {
            "example": {
                "doc_type": "All",
                "document_status": "ToReview",
                "page_number": 1,
                "page_size": 50,
                "sort_column": "status_date",
                "sort_order": "desc",
                "sla_type": "All"
            }
        }


class DocumentManagerItem(BaseModel):
    """
    Response item model - matches all columns returned by SP's #TempResults
    """
    fileid: Optional[int] = None
    fileuid: UUID
    type: Optional[str] = None
    filename: Optional[str] = None
    firm: Optional[int] = None
    entityuid: Optional[UUID] = None
    accountsid: Optional[str] = None
    accountuid: Optional[UUID] = None
    filepath: Optional[str] = None
    createdate: Optional[datetime] = None
    createtime: Optional[datetime] = None
    comments: Optional[str] = None
    createby: Optional[str] = None
    filenameframe: Optional[str] = None
    batchid: Optional[str] = None
    metadata: Optional[str] = None
    checksum: Optional[str] = None
    status: Optional[str] = None
    statusdate: Optional[datetime] = None
    method: Optional[str] = None
    reasonid: Optional[str] = None
    reason: Optional[str] = None
    harvestsystem: Optional[str] = None
    harvestmethod: Optional[str] = None
    harvestsource: Optional[str] = None
    indexsystem: Optional[str] = None
    indexmethod: Optional[str] = None
    extractsystem: Optional[str] = None
    extractmethod: Optional[str] = None
    age: Optional[int] = None
    emailsender: Optional[str] = None
    emailsubject: Optional[str] = None
    category: Optional[str] = None
    failurestage: Optional[str] = None
    filetypeproceesrule: Optional[str] = None
    filetypegenai: Optional[str] = None
    ignoredon: Optional[datetime] = None
    ignoredby: Optional[str] = None
    rule: Optional[str] = None
    businessdate: Optional[str] = None
    firmname: Optional[str] = None
    entityname: Optional[str] = None
    capturemethod: Optional[str] = None
    linkingmethod: Optional[str] = None
    stage: Optional[str] = None
    isactive: Optional[bool] = None
    updatefileid: Optional[UUID] = None
    statuscomment: Optional[str] = None
    duplicatefileid: Optional[UUID] = None
    fileprocessstage: Optional[str] = None
    businessruleapplieddate: Optional[datetime] = None
    fileextension: Optional[str] = None
    password: Optional[str] = None
    groupcode: Optional[str] = None
    replay: Optional[bool] = None
    lastattemptedtime: Optional[datetime] = None
    retrycount: Optional[int] = None
    ingestionfailedimageurl: Optional[str] = None
    created: Optional[datetime] = None
    createdby: Optional[str] = None
    updated: Optional[datetime] = None
    updatedby: Optional[str] = None
    age_sla_display: Optional[str] = None
    sla_status: Optional[str] = None
    tsla_status: Optional[str] = None
 
    class Config:
        from_attributes = True


class ApproveDocumentRequest(BaseModel):
    """
    Request item model - ApproveDocumentRequest
    """
    doc_uid: UUID = Field(description="Document UUID")
    comment: Optional[str] = Field(default=None, description="User comment")
    status: Optional[str] = Field(default=None, description="Document status")
    updated_by: Optional[str] = Field(default=None, description="Name of the use who approved document")


class UpdateDocumentReplayRequest(BaseModel):
    """
    Request model for /ReplayDocument and /AllReplayDocument Endpoints
    """
    doc_uid: UUID = Field(description="Document UUID")
    comment: Optional[str] = Field(default=None, description="User comment")
    updated_by: Optional[str] = Field(default=None, description="Name of the use who approved document")

    class Config:
        json_schema_extra = {
            "example": {
                "doc_uid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "comments": "string",
                "updated_by": "string"
            }
        }



class DocumentManagerResponse(BaseModel):
    """
    Complete API response with pagination info
    """
    total: int = Field(description="Total matching records")
    page: int = Field(description="Current page number")
    page_size: int = Field(description="Results per page")
    data: List[DocumentManagerItem] = Field(description="Document records")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total": 150,
                "page": 1,
                "page_size": 50,
                "data": []
            }
        }
