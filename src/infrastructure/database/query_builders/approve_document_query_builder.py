from typing import List
from uuid import UUID
from sqlalchemy import and_
from sqlalchemy.orm import Session
from src.domain.entities.file_manager import FileManager
from src.domain.entities.extract_file import ExtractFile

class ApproveDocumentQueryBuilder:
    """
    Query builder for ApproveDocument.
    Handles document retrieval, linked extract documents, and duplicate checking.
    """

    def __init__(self, db: Session, docuid: UUID):
        self.db = db
        self.docuid = docuid

    def get_document(self) -> FileManager | None:
        """
        Fetch the main document by DocUID
        """
        return (
            self.db.query(FileManager)
            .filter(FileManager.fileuid == self.docuid, FileManager.isactive.is_(True))
            .first()
        )

    def get_linked_extract_documents(self) -> List[ExtractFile]:
        """
        Fetch linked, active, non-ignored extract documents
        """
        return (
            self.db.query(ExtractFile)
            .filter(
                ExtractFile.fileuid == self.docuid,
                ExtractFile.isactive.is_(True),
                ExtractFile.islinked.is_(True),
                ExtractFile.isignored.is_(False),
            )
            .all()
        )

    def get_duplicate_sid(self) -> UUID | None:
        """
        Return the first Account_SID linked more than once
        """
        extract_docs = self.get_linked_extract_documents()
        sid_counts = {}
        for ed in extract_docs:
            sid_counts[ed.account_sid] = sid_counts.get(ed.account_sid, 0) + 1
        duplicate_sid = next((sid for sid, count in sid_counts.items() if count > 1), None)
        return duplicate_sid
