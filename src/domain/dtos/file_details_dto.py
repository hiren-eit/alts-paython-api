
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field

class FileDetailsItem(BaseModel):
    fileid: Optional[int] = None
    fileuid: Optional[UUID] = None
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

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

class FileDetailsResponse(BaseModel):
    total: int = Field(description="Total matching records")
    data: List[FileDetailsItem] = Field(description="File details")
