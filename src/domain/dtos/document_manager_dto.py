"""
Document Manager DTOs - Request/Response models for GetDocumentManager API
Mirrors all parameters and response fields from the SQL Server stored procedure.
"""
from datetime import date, datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class DocumentManagerFilter(BaseModel):
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
    total_count: int = Field(description="Total matching records")
    id: UUID
    status: Optional[str] = None
    status_date: Optional[datetime] = None
    type: Optional[str] = None
    ignored_on: Optional[datetime] = None
    ignored_by: Optional[str] = None
    rule: Optional[str] = None
    document_name: Optional[str] = None
    failure_stage: Optional[str] = None
    reason: Optional[str] = None
    age: Optional[int] = None
    sla_days: Optional[int] = None
    harvest_source: Optional[str] = None
    document_type_procees_rule: Optional[str] = None
    document_type_gen_ai: Optional[str] = None
    processing_method: Optional[str] = None
    capture_method: Optional[str] = None
    capture_system: Optional[str] = None
    email_sender: Optional[str] = None
    email_subject: Optional[str] = None
    linking_method: Optional[str] = None
    linking_system: Optional[str] = None
    extract_method: Optional[str] = None
    extract_system: Optional[str] = None
    batch: Optional[str] = None
    source_attributes: Optional[str] = None
    doc_uid: Optional[UUID] = None
    duplicate_document_id: Optional[UUID] = None
    stage: Optional[str] = None
    metadata: Optional[str] = None
    business_rule_applied_date: Optional[datetime] = None
    file_type: Optional[str] = None
    created: Optional[datetime] = None
    created_by: Optional[str] = None
    category: Optional[str] = None
    status_comment: Optional[str] = None
    
    # SLA calculated fields
    age_sla_display: Optional[str] = None  # e.g., "5/10"
    sla_status: Optional[str] = None  # "Within SLA", "On SLA", "SLA Breached"
    tsla_status: Optional[str] = None  # "T0", "T1", "T2", "T3", "T3+"
    
    # Ingestion counts
    ingestion_in_progress_count: Optional[int] = None
    ingestion_failed_count: Optional[int] = None
    manual_ingested_count: Optional[int] = None
    ingestion_done_count: Optional[int] = None
    total_ingestion_count: Optional[int] = None
    
    # Account info (from joins)
    firm_name: Optional[str] = None
    firm_id: Optional[str] = None
    entity_name: Optional[str] = None
    account_name: Optional[str] = None
    account_sid: Optional[str] = None
    account_uid: Optional[str] = None
    investor: Optional[str] = None
    businessdate: Optional[str] = None
    pub_uid: Optional[str] = None
    is_core_account: Optional[bool] = None
    
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
