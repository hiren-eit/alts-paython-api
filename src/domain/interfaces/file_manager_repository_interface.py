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
        Returns paginated file list with total count.
        Replicates the GetFileManager stored procedure logic.
        
        Returns:
            dict: {"total": int, "data": List[FileManagerItem]}
        """
        raise NotImplementedError

    def get_file_details_by_file_uid(
        self,
        db: Session,
        fileuid: UUID
    ) -> Dict:
        """
        Returns file details by fileuid.
        Replicates the GetFileDetailsByFileUID stored procedure logic.
        
        Returns:
            dict: {"total": int, "data": List[FileManagerItem]}
        """
        raise NotImplementedError

    def get_manual_extraction_config_fields_by_id(
        self,
        db: Session,
        fileconfigurationid: int
    ) -> Dict:
        """
        Returns manual extraction config fields by id.
        Replicates the GetManualExtractionConfigFieldsById stored procedure logic.
        
        Returns:
            dict: {"count": int, "resultobject": List, "resultcode": str}
        """
        raise NotImplementedError

    def get_extract_file_api(
        self,
        db: Session,
        fileuid: UUID
    ) -> Dict:
        """
        Returns extraction file details by fileuid.
        
        Returns:
            dict: ExtractionFileField data
        """
        raise NotImplementedError

    def get_extract_files_by_file_uid(
        self,
        db: Session,
        fileuid: UUID
    ) -> List[Dict]:
        """
        Returns list of extract files by file_uid.
        
        Returns:
            List[Dict]: List of ExtractFile data
        """
        raise NotImplementedError

    def add_file_comment(
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

    def update_extract_file_api(
        self,
        db: Session,
        request: UpdateExtractFileRequest
    ) -> ResponseObjectModel:
        """
        Skeleton for update_extract_file_api.
        """
        raise NotImplementedError
