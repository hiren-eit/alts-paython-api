from sqlalchemy.orm import Session
from uuid import UUID
from src.domain.entities.file_manager import FileManager

class IgnoreDocumentQueryBuilder:
    """
    Query builder for IgnoreDocument.
    Handles fetching the document by Id.
    """

    def __init__(self, db: Session, document_id: UUID):
        self.db = db
        self.document_id = document_id

    def get_document(self) -> FileManager | None:
        """
        Fetch the document by Id (read-only)
        """
        return (
            self.db.query(FileManager)
            .filter(FileManager.fileid == self.document_id)
            .first()
        )
