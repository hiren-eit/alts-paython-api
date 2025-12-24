from typing import Dict
from sqlalchemy.orm import Session
from src.domain.dtos.document_receiver_dto import DocumentRequestModel
from src.domain.interfaces.file_service_repository_interface import IFileServiceRepository
from src.domain.dtos.master_dto import Document
from src.domain.dtos.document_manager_dto import ApproveDocumentRequest, DocumentManagerFilter
from uuid import UUID

class FileOperationService:
    def __init__(self, repository: IFileServiceRepository):
        self.repo = repository

    def document_retrieval(
        self,
        db: Session,
        documents: DocumentRequestModel
    ) -> Dict:

        """
        Upload file.
        This endpoint replicates the /DocumentRetrieval API from .NET
        """
        return self.repo.document_retrieval(db, documents)
