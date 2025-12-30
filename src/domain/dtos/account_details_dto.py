from uuid import UUID
from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import date

class PublishingQueryParamsInput(BaseModel):
    accountid: Optional[UUID] = None
    filetype: Optional[str] = None
    pubstatus: Optional[str] = None
    orderbycolumn: Optional[str] = "Created"
    ordertype: Optional[str] = "ASC"

class PublishingRecordsResultResponse(BaseModel):
    publishingcontrolid: int
    account_uid: Optional[UUID] = None
    pub_status: Optional[str] = None
    business_date: Optional[date] = None
    expected_date: Optional[date] = None
    received_date: Optional[date] = None
    file_type: Optional[str] = None
    marketvalue: Optional[str] = None
    isactive: Optional[bool] = None
    created: Optional[Any] = None
    createdby: Optional[str] = None
    updated: Optional[Any] = None
    updatedby: Optional[str] = None

