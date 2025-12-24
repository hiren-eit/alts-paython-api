from typing import Optional
from sqlalchemy.orm import Session
from src.domain.entities.file_manager import FileManager

class DocumentDetailsQueryBuilder:
    """Builds the base query for Document details by DocUID."""

    def __init__(self, db: Session, doc_uid: str):
        self.db = db
        self.doc_uid = doc_uid
        self._query = None

    def build_query(self):
        # Build the base select from FileManager
        self._query = self.db.query(FileManager).filter(
            FileManager.fileuid == self.doc_uid
        )
        return self

    def get_one(self):
        return self._query.one_or_none()