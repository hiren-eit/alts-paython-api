from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

# If you have enums defined, replace the str types with those enums (e.g., SchemaTypes, ExtractionMethod, DataTypes)

class FileConfigurationLog(BaseModel):
    fileid: int
    created: datetime
    created_by: Optional[str]
    updated: Optional[datetime]
    updated_by: Optional[str]
    is_active: bool
    file_configuration_id: UUID
    title: Optional[str]
    description: Optional[str]
    file_configuration: Optional[str]  # replace with nested DTO if needed

class FileConfigurationField(BaseModel):
    fileid: int
    created: datetime
    created_by: Optional[str]
    updated: Optional[datetime]
    updated_by: Optional[str]
    is_active: bool
    field_name: Optional[str]
    data_type: str
    description: Optional[str]
    mandatory: Optional[bool]
    parent_field_id: Optional[UUID]
    sub_rows: List[str]
    file_configuration_id: Optional[UUID] = None

class FileConfiguration(BaseModel):
    fileid: Optional[int] = None
    created: Optional[datetime] = None
    created_by: Optional[str | int] = None
    updated: Optional[datetime] = None
    updated_by: Optional[str | int] = None
    is_active: Optional[bool] = None
    configuration_name: Optional[str] = None
    description: Optional[str] = None
    sla_priority: Optional[int] = None
    sla_days: Optional[int] = None
    schema_type: Optional[str] = None      # replace with SchemaTypes enum if available
    extraction: Optional[str] = None  # replace with ExtractionMethod enum if available
    file_type_id: Optional[UUID] = None
    reason: Optional[str] = None
    field_type: Optional[str] = None
    ingestion_code: Optional[int] = None
    fields_collection: Optional[List[FileConfigurationField]] = None
    logs_collection: Optional[List[FileConfigurationLog]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "fileid": 1,
                "created": "2025-12-15T09:14:17.977Z",
                "created_by": "string | int",
                "updated": "2025-12-15T09:14:17.977Z",
                "updated_by": "string | int",
                "is_active": True,
                "configuration_name": "string",
                "description": "string",
                "sla_priority": 0,
                "sla_days": 0,
                "schema_type": "LongForm",
                "extraction": "ComprehensiveExtraction",
                "file_type_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "reason": "string",
                "field_type": "string",
                "ingestion_code": 0,
                "fields_collection": [
                    {
                        "fileid": 1,
                        "created": "2025-01-01T00:00:00Z",
                        "created_by": "John Doe",
                        "updated": "2025-01-01T00:00:00Z",
                        "updated_by": "Jane Doe",
                        "is_active": True,
                        "field_name": "Field Name 1",
                        "data_type": "String",
                        "description": "Field description",
                        "mandatory": True,
                        "parent_field_id": "123e4567-e89b-12d3-a456-426614174000",
                        "sub_rows": ["Sub Row 1", "Sub Row 2"],
                        "file_configuration_id": "123e4567-e89b-12d3-a456-426614174000"
                    }
                ],
                "logs_collection": [
                    {
                        "fileid": 1,
                        "created": "2025-01-01T00:00:00Z",
                        "created_by": "John Doe",
                        "updated": "2025-01-01T00:00:00Z",
                        "updated_by": "Jane Doe",
                        "is_active": True,
                        "file_configuration_id": "123e4567-e89b-12d3-a456-426614174000",
                        "title": "Log Title 1",
                        "description": "Log description",
                        "file_configuration": "File configuration"
                    }
                ]
            }
        }

class FileConfigurationResponse(BaseModel):
    """
    Complete API response
    """
    result_code: str = Field(description="Result status of the API call") 
    total: int = Field(description="Total matching records")
    data: List[Dict] = Field(description="File configuration records")
    
    class Config:
        json_schema_extra = {
            "example": {
                "result_code": "SUCCESS",
                "total": 150,
                # "in_review_count": 1,
                "data": []
            }
        }