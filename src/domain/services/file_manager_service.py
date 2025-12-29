from sqlalchemy.orm import Session
from src.domain.interfaces.file_manager_repository_interface import IFileManagerRepository
from src.domain.dtos.file_manager_dto import FileManagerFilter
from src.domain.dtos.update_extract_file_dto import UpdateExtractFileRequest
from uuid import UUID


class FileManagerService:
    def __init__(self, repository: IFileManagerRepository):
        self.repo = repository

    def get_file_manager_list(self, db: Session, filters: FileManagerFilter):
        """
        Get paginated document manager list with filters.
        Replicates GetDocumentManager stored procedure logic.
        """
        return self.repo.get_file_manager_list(db, filters)

    def get_file_details_by_file_uid(self, db: Session, fileuid: UUID):
        """
        Get document details by fileuid.
        Replicates GetDocumentDetailsByDocUID stored procedure logic.
        """
        return self.repo.get_file_details_by_file_uid(db, fileuid)

    def get_manual_extraction_config_fields_by_id(self, db: Session, documentConfigurationId: int):
        """
        Get manual extraction config fields by id.
        Replicates GetManualExtractionConfigFieldsById stored procedure logic.
        """
        return self.repo.get_manual_extraction_config_fields_by_id(db, documentConfigurationId)

    def get_extract_document_api(self, db: Session, fileuid: UUID):
        """
        Get extract document api.
        """
        return self.repo.get_extract_document_api(db, fileuid)

    def get_extract_documents_by_file_uid(self, db: Session, fileuid: UUID):
        """
        Get extract documents by file_uid.
        Replicates GetExtractDocumentsByDocUIDAsync logic.
        """
        return self.repo.get_extract_documents_by_file_uid(db, fileuid)

    def add_document_comment(self, db: Session, fileuid: UUID, comment: str, createdby: str):
        """
        Add a comment to a document.
        """
        return self.repo.add_document_comment(db, fileuid, comment, createdby)

    def update_extract_document_api(self, db: Session, request: UpdateExtractFileRequest):
        """
        Skeleton for UpdateExtractDocumentApi.
        """
        return self.repo.update_extract_document_api(db, request)
