from abc import ABC, abstractmethod
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from src.domain.dtos.file_activity_dto import FileActivity

class IFileActivityRepository(ABC):
    """Interface for FileActivity Repository"""
    
    @abstractmethod
    def get_file_activity(self, db: Session, docuid: UUID) -> List[FileActivity]:
        """
        Get file activity logs by docuid.
        Replicates GetDocumentActivityByDocUID stored procedure logic.
        """
        pass
