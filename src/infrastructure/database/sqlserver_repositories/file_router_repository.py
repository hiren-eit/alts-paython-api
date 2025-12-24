from typing import List, Any
from sqlalchemy.orm import Session
from src.domain.interfaces.file_router_repository_interface import IFileRouterRepository
from src.domain.entities.extract_file import ExtractFile
from src.infrastructure.logging.logger_manager import get_logger
from uuid import UUID

logger = get_logger(__name__)

class FileRouterRepository(IFileRouterRepository):
    """SQL Server implementation of FileRouter repository using SQLAlchemy ORM"""

    def get_multiple_entities_or_investor(
        self,
        db: Session,
        file_uid: UUID
    ) -> List[ExtractFile]:
        """
        Replicates GetMultipleEntitiesORInvestor logic.
        """
        try:
            logger.info(f"Fetching ExtractDocuments with file_uid: {file_uid}")

            results = db.query(ExtractFile).filter(
                ExtractFile.fileuid == file_uid
            ).all()

            logger.info(f"Successfully fetched {len(results)} ExtractDocuments with file_uid: {file_uid}")
            return results
        except Exception as ex:
            logger.error(f"An error occurred while fetching ExtractDocuments with file_uid: {file_uid}. Exception: {ex}", exc_info=True)
            raise
