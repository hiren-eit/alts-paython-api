from datetime import datetime
from src.domain.entities.file_manager import FileManager

class IgnoreDocumentResultEnricher:
    """
    Enriches the document entity for ignoring.
    Sets the ignore fields, status, and updated timestamps.
    """

    def enrich(self, file: FileManager, comment: str | None = None, updated_by: str = "SYSTEM") -> FileManager:
        file.ignoredby = len(updated_by)
        file.ignoredon = datetime.utcnow()
        file.comments = comment
        file.updatedby = len(updated_by)
        file.updated = datetime.utcnow()
        file.status = "Ignored"
        file.statusdate = datetime.utcnow()
        return file
