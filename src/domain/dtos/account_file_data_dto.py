from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from typing import Optional, List, Any

class AccountFileDataResponse(BaseModel):
    fileuid: Optional[UUID]
    account_uid: Optional[UUID]
    accounts_id: Optional[str]
    entity_uid: Optional[UUID]
    firm_id: Optional[int]
    entity_name: Optional[str]
    account_name: Optional[str]
    firm_name: Optional[str]
    investor: Optional[str]
    frequency: Optional[str]
    delay: Optional[int]
    annual_delay: Optional[int]
    created: Optional[datetime]
    updated: Optional[datetime]
