"""
Resolve File Update DTOs - Request model for ResolveFileUpdate API
Mirrors all parameters and response fields from the SQL Server stored procedure.
"""
from datetime import date, datetime
from typing import List, Optional, Any
from uuid import UUID
from pydantic import BaseModel, Field

class ResolveFileUpdate(BaseModel):
    """
    Request resolve file update
    """
    selected_file_uid: UUID
    ignored_file_uid: UUID
    is_update_selected: bool
    updatedby: Optional[str] = None


class ResolveFileUpdateResponseDTO(BaseModel):
    result_code: Optional[str] = None
    # total: Optional[int] = 0
    # data: Any = None
    result_message: Optional[str] = None
