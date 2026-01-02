"""
File Manager DTOs - Request/Response models for GetFileManager API
Mirrors all parameters and response fields from the SQL Server stored procedure.
"""

from pydantic.types import UUID4
from datetime import date, datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class FileManagerFilter(BaseModel):
    """
    Request filter model - matches all SP parameters:
    @FileType, @FileStatus, @FilterJson, @PageNumber, @PageSize,
    @SortColumn, @SortOrder, @Visibility, @SlaType
    """

    # Core SP parameters
    file_type: str = Field(default="All", description="File type filter")
    file_status: str = Field(
        default="ToReview",
        description="Tab/status filter: All, ToReview, Approved, captured, extracted, linked, ingested, duplicates, completed, INPROGRESS, IGNORED",
    )
    page_number: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(default=100, ge=1, le=1000, description="Results per page")
    sort_column: Optional[str] = Field(default=None, description="Column to sort by")
    sort_order: Optional[str] = Field(
        default="desc", description="Sort order: asc or desc"
    )
    visibility: str = Field(
        alias="visiblity",
        default="S",
        description="Visibility mode: S for tokenized, D for detokenized",
    )
    sla_type: str = Field(
        default="All",
        description="SLA filter: All, withinsla, onsla, slabreached, uncategorized",
    )

    # FilterJson fields - parsed from JSON in SP
    search_text: Optional[List[str]] = Field(
        alias="SearchText",
        default=None,
        description="Search text(s) for filename, fileuid, emailsubject, etc.",
    )
    firm_ids: Optional[List[int]] = Field(
        alias="FirmIds", default=None, description="Firm ID filter"
    )
    entity_ids: Optional[List[str]] = Field(
        alias="EntityIds", default=None, description="Entity UID filter"
    )
    file_types: Optional[List[str]] = Field(
        alias="FileTypes", default=None, description="File extension filter"
    )
    file_type_gen_ai: Optional[List[str]] = Field(
        alias="FileTypeGenAi", default=None, description="GenAI file type filter"
    )
    file_type_procees_rule: Optional[List[str]] = Field(
        alias="FileTypeProcessRule",
        default=None,
        description="Process rule file type filter",
    )
    file_uids: Optional[List[str]] = Field(
        alias="FileUids", default=None, description="File UID filter"
    )
    status_comments: Optional[List[str]] = Field(
        alias="StatusComments", default=None, description="Status comment filter"
    )
    failure_stages: Optional[List[str]] = Field(
        alias="FailureStages", default=None, description="Failure stage filter"
    )
    reasons: Optional[List[str]] = Field(
        alias="Reasons", default=None, description="Reason filter"
    )
    last_stages: Optional[List[str]] = Field(
        alias="LastStages", default=None, description="Last stage filter"
    )
    processing_methods: Optional[List[str]] = Field(
        alias="ProcessingMethods", default=None, description="Processing method filter"
    )
    capture_methods: Optional[List[str]] = Field(
        alias="CaptureMethods", default=None, description="Capture method filter"
    )
    capture_systems: Optional[List[str]] = Field(
        alias="CaptureSystems", default=None, description="Capture system filter"
    )
    extract_methods: Optional[List[str]] = Field(
        alias="ExtractMethods", default=None, description="Extract method filter"
    )
    extract_systems: Optional[List[str]] = Field(
        alias="ExtractSystems", default=None, description="Extract system filter"
    )
    senders: Optional[List[str]] = Field(
        alias="Senders", default=None, description="Email sender filter"
    )
    subjects: Optional[List[str]] = Field(
        alias="Subjects", default=None, description="Email subject filter"
    )
    ignored_by: Optional[List[str]] = Field(
        alias="IgnoredBy", default=None, description="Ignored by user filter"
    )
    account_sids: Optional[List[str]] = Field(
        alias="AccountSids", default=None, description="Account SID filter"
    )
    account_uids: Optional[List[str]] = Field(
        alias="AccountUids", default=None, description="Account UID filter"
    )
    investors: Optional[List[str]] = Field(
        alias="Investors", default=None, description="Investor filter"
    )
    account_names: Optional[List[str]] = Field(
        alias="AccountNames", default=None, description="Account name filter"
    )
    investor: Optional[str] = Field(alias="Investor", default=None)
    account_name: Optional[str] = Field(alias="AccountName", default=None)
    firm_id: Optional[int] = Field(alias="FirmID", default=None)
    entity_uid: Optional[str] = Field(alias="EntityUID", default=None)

    # Date range filters
    filter_created_date_from: Optional[date] = Field(
        default=None, description="Created date from"
    )
    filter_created_date_to: Optional[date] = Field(
        default=None, description="Created date to"
    )
    filter_status_date_from: Optional[date] = Field(
        default=None, description="Status date from"
    )
    filter_status_date_to: Optional[date] = Field(
        default=None, description="Status date to"
    )
    filter_business_date_from: Optional[date] = Field(
        default=None, description="Business date from"
    )
    filter_business_date_to: Optional[date] = Field(
        default=None, description="Business date to"
    )

    # Single value filters
    source: Optional[str] = Field(default=None, description="Harvest source filter")
    linking_method: Optional[str] = Field(
        default=None, description="Linking method filter"
    )
    batch_id: Optional[str] = Field(default=None, description="Batch ID filter")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "file_type": "All",
                "file_status": "ToReview",
                "page_number": 1,
                "page_size": 50,
                "sort_column": "status_date",
                "sort_order": "desc",
                "sla_type": "All",
            }
        }


class FileManagerItem(BaseModel):
    """
    Response item model - matches all columns returned by SP's #TempResults
    """

    fileid: Optional[int] = None
    fileuid: UUID
    type: Optional[str] = None
    filename: Optional[str] = None
    firm: Optional[int] = None
    entityuid: Optional[UUID] = Field(alias="entityUid", default=None)
    accountsid: Optional[str] = None
    accountuid: Optional[str] = None
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
    sladays: Optional[int] = Field(alias="SLADays", default=None)
    emailsender: Optional[str] = None
    emailsubject: Optional[str] = None
    category: Optional[str] = None
    failurestage: Optional[str] = None
    filetypeprocessrule: Optional[str] = None
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
    investor: Optional[str] = None
    accountname: Optional[str] = None
    entityuids: Optional[str] = None
    pubuid: Optional[str] = None
    firmid: Optional[str] = Field(alias="firmID", default=None)
    iscoreaccount: Optional[bool] = None
    totalingestioncount: Optional[str] = None
    ingestioninprogresscount: Optional[int] = None
    ingestionfailedcount: Optional[int] = None
    manualingestedcount: Optional[int] = None
    ingestiondonecount: Optional[int] = None

    class Config:
        from_attributes = True
        populate_by_name = True


class ApproveFileRequest(BaseModel):
    """
    Request item model - ApproveFileRequest
    """

    fileUid: UUID = Field(description="File UUID")
    comment: Optional[str] = Field(default=None, description="User comment")
    status: Optional[str] = Field(default=None, description="File status")
    updatedby: Optional[str] = Field(
        default=None, description="Name of the use who approved file"
    )


class ReplayFileRequestDTO(BaseModel):
    fileuids: List[UUID4] = Field(
        ..., description="List of unique file identifiers to replay"
    )
    comment: Optional[str] = Field(None, description="Comment or reason for replay")
    updatedby: Optional[str] = Field("SYSTEM", description="User initiating the replay")


class FileManagerResponse(BaseModel):
    """
    Complete API response with pagination info
    """

    total: int = Field(description="Total matching records")
    page: int = Field(description="Current page number")
    page_size: int = Field(description="Results per page")
    data: List[FileManagerItem] = Field(description="File records")

    class Config:
        json_schema_extra = {
            "example": {"total": 150, "page": 1, "page_size": 50, "data": []}
        }


class IgnoreFilesRequest(BaseModel):
    fileuids: str
    status: str
    updated_by: Optional[str] = None
    comments: Optional[str] = None
