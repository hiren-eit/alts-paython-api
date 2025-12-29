from typing import Optional
from sqlalchemy.orm import Session
from src.domain.entities.file_manager import FileManager

class FileDetailsQueryBuilder:
    """Builds the base query for File details by FileUID."""

    def __init__(self, db: Session, file_uid: str):
        self.db = db
        self.file_uid = file_uid
        self._query = None

    def build_query(self):
        # Build the base select from FileManager
        self._query = self.db.query(FileManager).filter(
            FileManager.fileuid == self.file_uid
        )
        return self

    def get_one(self):
        return self._query.one_or_none()