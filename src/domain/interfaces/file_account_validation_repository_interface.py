from src.domain.dtos.file_account_validation_dto import FileAccountValidation
from abc import ABC, abstractmethod
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session 

class IFileAccountValidationRepository(ABC):
    """Interface for FileActivity Repository"""
    
    @abstractmethod
    def get_file_account_details(self, db: Session, fileuid: UUID) -> List[FileAccountValidation]:
        """
        Get file account details by fileuid.
        """
        pass
