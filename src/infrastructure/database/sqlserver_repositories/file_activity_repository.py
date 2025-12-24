from typing import List
from uuid import UUID
from sqlalchemy.orm import Session

from src.domain.interfaces.file_activity_repository_interface import IFileActivityRepository
from src.domain.dtos.file_activity_dto import FileActivity
from src.infrastructure.logging.logger_manager import get_logger

logger = get_logger(__name__)

class FileActivityRepository(IFileActivityRepository):
    """SQL Server implementation of FileActivity repository"""

    def get_file_activity(self, db: Session, docuid: UUID) -> List[FileActivity]:
        """
        Skeleton implementation for GetFileActivityLogs.
        """
        try:
            logger.info(f"SQL Server: GetFileActivityLogs called for {docuid}")
            # Return empty list as skeleton
            return []
        except Exception as ex:
            logger.error(f"SQL Server: GetFileActivityLogs error: {ex}", exc_info=True)
            raise
