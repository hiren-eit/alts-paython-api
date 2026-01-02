from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from decimal import Decimal


class ValidationDetailDto(BaseModel):
    validation_type: Optional[str] = None
    description: Optional[str] = None
    newport_value: Optional[Decimal] = None
    extract_value: Optional[Decimal] = None
    difference: Optional[Decimal] = None
    status: Optional[str] = None
