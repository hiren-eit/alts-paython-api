from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from src.domain.interfaces.file_activity_repository_interface import IFileActivityRepository
from src.domain.dtos.file_activity_dto import FileActivityResponse

class FileActivityService:
    def __init__(self, repository: IFileActivityRepository):
        self.repo = repository

    def get_file_activity_logs(self, db: Session, fileuid: UUID) -> List[FileActivityResponse]:
        """
        Get file activity logs.
        """
        return self.repo.get_file_activity(db, fileuid)
