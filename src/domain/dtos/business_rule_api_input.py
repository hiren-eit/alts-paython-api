from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import date

class GetBusinessRuleApiInput(BaseModel):
    RuleType: str
    SourceType: Optional[str] = "all"
    ContentType: Optional[int] = None
    PageNumber: int = 1
    PageSize: int = 50
    SortColumn: Optional[str] = "Created"
    SortOrder: Optional[str] = "DESC"
    SearchText: Optional[str] = None
    FilterStatus: Optional[str] = None
    FilterCreatedBy: Optional[str] = None
    FilterSenderAddress: Optional[str] = None
    FilterRuleID: Optional[str] = None
    FilterSubject: Optional[str] = None
    FilterEmailBody: Optional[str] = None
    FilterCreatedFrom: Optional[date] = None
    FilterCreatedTo: Optional[date] = None
