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
        Get paginated file manager list with filters.
        Replicates GetFileManager stored procedure logic.
        """
        return self.repo.get_file_manager_list(db, filters)

    def get_file_details_by_file_uid(self, db: Session, fileuid: UUID):
        """
        Get file details by fileuid.
        Replicates GetFileDetailsByFileUID stored procedure logic.
        """
        return self.repo.get_file_details_by_file_uid(db, fileuid)

    def get_manual_extraction_config_fields_by_id(self, db: Session, fileConfigurationId: int):
        """
        Get manual extraction config fields by id.
        Replicates GetManualExtractionConfigFieldsById stored procedure logic.
        """
        return self.repo.get_manual_extraction_config_fields_by_id(db, fileConfigurationId)

    def get_extract_file_api(self, db: Session, fileuid: UUID):
        """
        Get extract file api.
        """
        return self.repo.get_extract_file_api(db, fileuid)

    def get_extract_files_by_file_uid(self, db: Session, fileuid: UUID):
        """
        Get extract files by file_uid.
        Replicates GetExtractFilesByFileUIDAsync logic.
        """
        return self.repo.get_extract_files_by_file_uid(db, fileuid)

    def add_file_comment(self, db: Session, fileuid: UUID, comment: str, createdby: str):
        """
        Add a comment to a file.
        """
        return self.repo.add_file_comment(db, fileuid, comment, createdby)

    def update_extract_file_api(self, db: Session, request: UpdateExtractFileRequest):
        """
        Skeleton for UpdateExtractFileApi.
        """
        return self.repo.update_extract_file_api(db, request)
