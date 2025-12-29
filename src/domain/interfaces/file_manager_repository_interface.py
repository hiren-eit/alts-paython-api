from typing import List, Any, Dict
from sqlalchemy.orm import Session
from src.domain.dtos.file_manager_dto import FileManagerFilter
from src.domain.dtos.update_extract_file_dto import UpdateExtractFileRequest, ResponseObjectModel
from uuid import UUID


class IFileManagerRepository:
    """Repository interface for FileManager"""

    def get_file_manager_list(
        self, 
        db: Session, 
        filters: FileManagerFilter
    ) -> Dict:
        """
        Returns paginated document list with total count.
        Replicates the GetDocumentManager stored procedure logic.
        
        Returns:
            dict: {"total": int, "data": List[DocumentManagerItem]}
        """
        raise NotImplementedError

    def get_file_details_by_file_uid(
        self,
        db: Session,
        fileuid: UUID
    ) -> Dict:
        """
        Returns document details by fileuid.
        Replicates the GetDocumentDetailsByDocUID stored procedure logic.
        
        Returns:
            dict: {"total": int, "data": List[DocumentManagerItem]}
        """
        raise NotImplementedError

    def get_manual_extraction_config_fields_by_id(
        self,
        db: Session,
        documentConfigurationId: int
    ) -> Dict:
        """
        Returns manual extraction config fields by id.
        Replicates the GetManualExtractionConfigFieldsById stored procedure logic.
        
        Returns:
            dict: {"count": int, "resultobject": List, "resultcode": str}
        """
        raise NotImplementedError

    def get_extract_document_api(
        self,
        db: Session,
        fileuid: UUID
    ) -> Dict:
        """
        Returns extraction document details by fileuid.
        
        Returns:
            dict: ExtractionDocumentField data
        """
        raise NotImplementedError

    def get_extract_documents_by_file_uid(
        self,
        db: Session,
        fileuid: UUID
    ) -> List[Dict]:
        """
        Returns list of extract documents by file_uid.
        
        Returns:
            List[Dict]: List of ExtractDocument data
        """
        raise NotImplementedError

    def add_document_comment(
        self,
        db: Session,
        fileuid: UUID,
        comment: str,
        createdby: str
    ) -> bool:
        """
        Updates FileManager record with a comment.
        """
        raise NotImplementedError

    def update_extract_document_api(
        self,
        db: Session,
        request: UpdateExtractFileRequest
    ) -> ResponseObjectModel:
        """
        Skeleton for UpdateExtractDocumentApi.
        """
        raise NotImplementedError
