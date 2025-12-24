from typing import Dict
from sqlalchemy.orm import Session
from src.domain.dtos.document_receiver_dto import DocumentRequestModel
from src.domain.dtos.master_dto import ResolveUpdateInputModel

class IFileServiceRepository:
    """Repository interface for FileService"""

    def document_retrieval(
        self,
        db: Session,
        documents: DocumentRequestModel
    ) -> Dict:
        """
        Upload file.
        This endpoint replicates the /DocumentRetrieval API from .NET
        """
        raise NotImplementedError