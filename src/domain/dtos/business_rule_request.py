
from uuid import UUID
from pydantic import BaseModel
from typing import Optional

class BusinessRuleRequest(BaseModel):
    businessruleid: Optional[int] = None
    ruleexpressions: str
    ruletype: str
    sourceid: Optional[int] = None
    uniqueruleid: Optional[str] = None
    isactive: bool
    password: Optional[str] = None
    groupcode: Optional[str] = None
    reasonfortoggle: Optional[str] = None
    filetypeid: Optional[int] = None
    usage: Optional[int] = None
