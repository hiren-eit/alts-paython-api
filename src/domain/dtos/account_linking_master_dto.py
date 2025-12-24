from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field

class AccountLinkingMasterDataInputModel(BaseModel):
    type: Optional[str] = None
    newport_value: Optional[str] = None
    new_name: Optional[str] = None
    investor: Optional[str] = None
    fund: Optional[str] = None
    status: Optional[str] = None
    created_start: Optional[datetime] = None
    created_end: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_start: Optional[datetime] = None
    updated_end: Optional[datetime] = None
    updated_by: Optional[str] = None
    reviewed_start: Optional[datetime] = None
    reviewed_end: Optional[datetime] = None
    reviewed_by: Optional[str] = None
    is_active: Optional[bool] = None
    unique_rule_id: Optional[str] = None
    search_text: Optional[str] = None
    page_index: Optional[int] = 1
    page_size: Optional[int] = 50
    sort_column: Optional[str] = "Created"
    sort_direction: Optional[str] = "DESC"
    creation_doc_uid: Optional[UUID] = None

    class Config:
        json_schema_extra = {
            "example": {
                "type": "Account",
                "newport_value": "ACC-123",
                "new_name": "New Account Name",
                "investor": "Investor A",
                "fund": "Fund X",
                "status": "Pending",
                "created_start": "2025-01-01T00:00:00Z",
                "created_end": "2025-02-01T00:00:00Z",
                "created_by": "jane.doe",
                "updated_start": "2025-01-05T00:00:00Z",
                "updated_end": "2025-02-05T00:00:00Z",
                "updated_by": "john.doe",
                "reviewed_start": "2025-01-10T00:00:00Z",
                "reviewed_end": "2025-02-10T00:00:00Z",
                "reviewed_by": "reviewer1",
                "is_active": True,
                "unique_rule_id": "RULE-001",
                "search_text": "search keyword",
                "page_index": 1,
                "page_size": 50,
                "sort_column": "Created",
                "sort_direction": "DESC",
                "creation_doc_uid": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
            }
        }


class AccountLinkingMaster(BaseModel):
    type: Optional[str] = None
    newport_value: Optional[str] = None
    new_name: Optional[str] = None
    reason_for_toggle: Optional[str] = None
    unique_rule_id: Optional[str] = None
    status: Optional[str] = None
    reviewed: Optional[datetime] = None
    reviewed_by: Optional[str] = "SYSTEM"
    creation_doc_uid: Optional[UUID] = None
    id: UUID = Field(default_factory=UUID, description="Unique identifier for the entity")
    created: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    created_by: Optional[str] = "SYSTEM"
    updated: Optional[datetime] = None
    updated_by: Optional[str] = None
    is_active: bool = True

    class Config:
        json_schema_extra = {
            "example": {
                "type": "Account",
                "newport_value": "ACC-123",
                "new_name": "New Account Name",
                "reason_for_toggle": "Mismatch resolved",
                "unique_rule_id": "RULE-001",
                "status": "Approved",
                "reviewed": "2025-01-15T12:00:00Z",
                "reviewed_by": "SYSTEM",
                "creation_doc_uid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "created": "2025-01-10T10:00:00Z",
                "created_by": "SYSTEM",
                "updated": "2025-01-12T12:00:00Z",
                "updated_by": "jane.doe",
                "is_active": True
            }
        }


class BatchRuleUpdateRequest(BaseModel):
    rule_ids: List[UUID]  # List of UUIDs for RuleIds
    status: str  # "Approve" or "Ignore"
    updated_by: str

    class Config:
        # Convert camelCase to snake_case automatically
        json_schema_extra = {
            "example": {
                "rule_ids": [
                    "123e4567-e89b-12d3-a456-426614174000",
                    "223e4567-e89b-12d3-a456-426614174001"
                ],
                "status": "Approve",
                "updated_by": "jane doe"
            }
        }


class AccountLinkingMasterResponse(BaseModel):
    result_code: Optional[str] = Field(default=None, description="Result code of an API call")
    total: int = Field(description="Total matching records")
    in_review_count: int = Field(description="Total records that are in review")
    data: Optional[List[dict]] = Field(default=None, description="Account Linking Master Data")
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
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "type": "Account",
                            "newport_value": "ACC-123",
                            "new_name": "New Account Name",
                            "status": "Approved",
                            "created": "2025-01-10T10:00:00Z",
                            "updated": "2025-01-12T12:00:00Z",
                            "is_active": True
                        }
                    ],
                    "page_index": 1,
                    "page_size": 50
                },
                "result_message": ""
            }
        }