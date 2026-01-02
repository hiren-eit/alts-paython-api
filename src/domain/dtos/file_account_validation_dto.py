from src.domain.dtos.validation_detail_dto import ValidationDetailDto
from pydantic import BaseModel
from typing import Optional, List, Any

class FileAccountValidation(BaseModel):
    account_sid: int
    total_validation_count: int
    passed_validation_count: int
    balance_checks: List[ValidationDetailDto] = []
    other_checks: List[ValidationDetailDto] = []