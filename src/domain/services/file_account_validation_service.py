from src.domain.interfaces.file_account_validation_repository_interface import IFileAccountValidationRepository
from src.domain.dtos.file_account_validation_dto import FileAccountValidation
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session

class FileAccountValidationService:
    def __init__(self, repository: IFileAccountValidationRepository):
        self.repo = repository

    def get_file_account_details(self, db: Session, fileuid: UUID) -> List[FileAccountValidation]:
        """
        Get file account validation details.
        """
        return self.repo.get_file_account_details(db, fileuid)
