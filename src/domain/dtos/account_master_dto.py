"""
Account Master DTOs - Request/Response models for AccountMaster API
Mirrors all parameters and response fields from the SQL Server stored procedure.
"""
from datetime import date, datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

class AccountMasterListInputModel(BaseModel):
    """
    Account Master List Input model - matches all SP parameters:
    @PageNumber, @PageSize, @SortColumn, @SortOrder, @SearchText,
    @AccountUID, @AccountSID, @Visibility
    """
    # Core SP parameters
    visibility: Optional[str] = Field(default="S", description="Visibility option for GetAccountMasterListApi SP")
    page_number: int = Field(default=1, description="Page number (1-indexed)")
    page_size: int = Field(default=50, description="Results per page")
    sort_column: str = Field(default="Created", description="Column to sort by")
    sort_order: str = Field(default="DESC", description="Sort order: asc or desc")
    search_text: Optional[str] = Field(default=None, description="Text to search")
    account_uid: Optional[UUID] = Field(default=None, description="Account UID")
    account_sid: Optional[str] = Field(default=None, description="Account SID")


class AccountMaster(BaseModel):
    id: UUID
    created: datetime = Field(default_factory=datetime.utcnow, description="Created UTC time")
    created_by: Optional[str] = Field(default="SYSTEM", max_length=255, description="Creator")
    updated: Optional[datetime] = Field(default=None, description="Last updated time")
    updated_by: Optional[str] = Field(default=None, max_length=255, description="Last updater")
    is_active: bool = Field(default=True, description="Active flag")

    # AccountMaster-specific fields
    account_uid: Optional[UUID] = Field(default=None, description="Account UID")
    account_sid: Optional[str] = Field(default=None, description="Account SID")
    entity_uid: Optional[UUID] = Field(default=None, description="Entity UID")
    firm_id: Optional[int] = Field(default=None, description="Firm ID")
    frequency: Optional[str] = Field(default=None, description="Frequency")
    delay: Optional[int] = Field(default=None, description="Delay")
    annual_delay: Optional[int] = Field(default=None, description="Annual delay")
    account_name: Optional[str] = Field(default=None, description="Account name")
    investor: Optional[str] = Field(default=None, description="Investor")
    tokenized_account_name: Optional[str] = Field(default=None, description="Tokenized account name")
    tokenized_investor: Optional[str] = Field(default=None, description="Tokenized investor")
    entity_name: Optional[str] = Field(default=None, description="Entity name")
    firm_name: Optional[str] = Field(default=None, description="Firm name")
    create_date: Optional[datetime] = Field(default=None, description="Create date")
    account_status: Optional[str] = Field(default=None, description="Account status")
    account_status_date: Optional[datetime] = Field(default=None, description="Account status date")
    source_uid: Optional[UUID] = Field(default=None, description="Source UID")
    institution_name: Optional[str] = Field(default=None, description="Institution name")
    manager_type: Optional[str] = Field(default=None, description="Manager type")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "created": "2025-12-17T11:20:11.384Z",
                "created_by": "string",
                "updated": "2025-12-17T11:20:11.384Z",
                "updated_by": "string",
                "is_active": True,
                "account_uid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "account_sid": "string",
                "entity_uid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "firm_id": 0,
                "frequency": "string",
                "delay": 0,
                "annual_delay": 0,
                "account_name": "string",
                "investor": "string",
                "tokenized_account_name": "string",
                "tokenized_investor": "string",
                "entity_name": "string",
                "firm_name": "string",
                "create_date": "2025-12-17T11:20:11.384Z",
                "account_status": "string",
                "account_status_date": "2025-12-17T11:20:11.384Z",
                "source_uid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "institution_name": "string",
                "manager_type": "string"
            }
        }

class AccountMasterResponse(BaseModel):
    result_code: Optional[str] = Field(default=None, description="Result code of an API call")
    total: int = Field(description="Total matching records")
    in_review_count: int = Field(description="Total records that are in review")
    data: Optional[List[dict]] = Field(default=None, description="Account Master Data")
    result_message: Optional[str] = Field(default=None, description="Result Message")

    class Config:
        # Allows C#-style camelCase in request/response payloads
        json_schema_extra = {
            "example": {
                "result_code": "Success",
                "total": 1,
                "in_review_count": 1,
                "data": {
                    "items": [
                        {}
                    ],
                    "page_index": 1,
                    "page_size": 50
                },
                "result_message": ""
            }
        }
