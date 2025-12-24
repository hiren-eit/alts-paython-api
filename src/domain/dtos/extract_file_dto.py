from pydantic import BaseModel, Field
from typing import List, Optional, Any
from uuid import UUID
from datetime import date

class ExtractDocument(BaseModel):
    recid: Optional[int] = None
    fileuid: UUID
    fileconfigurationid: Optional[UUID] = None
    filetype: Optional[str] = None
    extracteddata: Optional[str] = None
    investor: Optional[str] = None
    account: Optional[str] = None
    account_uid: Optional[UUID] = None
    account_sid: Optional[str] = None
    firm_id: Optional[int] = None
    entity_uid: Optional[UUID] = None
    token: Optional[str] = None
    ingestiontoken: Optional[str] = None
    businessdate: Optional[date] = None
    islinked: bool
    isignored: bool
    ignorecomment: Optional[str] = None
    batchid: Optional[str] = None
    ingestionstatus: Optional[str] = None
    ismanualingested: Optional[bool] = None
    ingestedby: Optional[str] = None
    isactive: bool

    class Config:
        from_attributes = True

class FileConfigurationFieldDTO(BaseModel):
    """DTO for file configuration field"""
    fileconfigurationfieldid: Optional[int] = None
    fileconfigurationid: Optional[int] = None
    name: Optional[str] = None
    datatype: Optional[str] = None
    isactive: Optional[bool] = None
    description: Optional[str] = None
    mandatory: Optional[bool] = None
    parent_field_id: Optional[int] = None

    class Config:
        from_attributes = True

class FileSecurityMappingDTO(BaseModel):
    """DTO for file security mapping"""
    id: Optional[int] = None
    fileuid: Optional[UUID] = None
    security: Optional[str] = None
    ticker: Optional[str] = None
    cusip: Optional[str] = None
    units: Optional[float] = None
    lastprice: Optional[float] = None
    marketvalue: Optional[float] = None
    currency: Optional[str] = None
    accruedinterest: Optional[float] = None
    status: Optional[str] = None
    comment: Optional[str] = None
    ismissingsecurity: Optional[bool] = None
    securitystage: Optional[str] = None
    documentname: Optional[str] = None
    isactive: Optional[bool] = None
    created: Optional[Any] = None
    createdby: Optional[str] = None
    updated: Optional[Any] = None
    updatedby: Optional[str] = None

    class Config:
        from_attributes = True

class ExtractionFileDetailDTO(BaseModel):
    """DTO for extraction file detail"""
    recid: Optional[int] = None
    fileuid: Optional[UUID] = None
    classification: Optional[str] = None
    extraction_data: Optional[str] = None
    bounding_box_data: Optional[str] = None
    confidence_scores: Optional[str] = None
    duplicate_flag: Optional[bool] = None
    duplicate_file_id: Optional[UUID] = None
    update_flag: Optional[bool] = None
    update_file_id: Optional[UUID] = None
    message: Optional[str] = None
    timestamp: Optional[str] = None
    status: Optional[bool] = None
    isupdate: Optional[bool] = None
    type: Optional[str] = None
    ismanual: Optional[bool] = None
    isadd: Optional[bool] = None
    isactive: Optional[bool] = None
    created: Optional[Any] = None
    createdby: Optional[str] = None
    updated: Optional[Any] = None
    updatedby: Optional[str] = None

    class Config:
        from_attributes = True

class ExtractionDocumentField(BaseModel):
    """
    Main DTO for extraction document field response.
    Equivalent to ExtractionDocumentField in .NET
    """
    extraction_document_detail: Optional[ExtractionFileDetailDTO] = None
    configuration: Optional[str] = None
    file_security_mappings: Optional[List[FileSecurityMappingDTO]] = None
    file_configuration_fields: Optional[List[FileConfigurationFieldDTO]] = None
    object_fields: Optional[List[FileConfigurationFieldDTO]] = None
    total_field_list: Optional[int] = None
    missing_field_list: Optional[int] = None
    configuration_id: Optional[int] = None
    update_file_id: Optional[str] = None

    class Config:
        from_attributes = True
