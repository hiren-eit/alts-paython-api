from abc import ABC, abstractmethod
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from src.domain.dtos.file_activity_dto import FileActivityResponse

class IFileActivityRepository(ABC):
    """Interface for FileActivity Repository"""
    
    @abstractmethod
    def get_file_activity(self, db: Session, fileuid: UUID) -> List[FileActivityResponse]:
        """
        Get file activity logs by fileuid.
        Replicates GetFileActivityByFileUID stored procedure logic.
        """
        pass
