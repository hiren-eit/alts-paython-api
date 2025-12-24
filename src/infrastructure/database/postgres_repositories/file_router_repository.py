from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from src.domain.interfaces.file_router_repository_interface import IFileRouterRepository
from src.domain.entities.extract_file import ExtractFile
from src.infrastructure.logging.logger_manager import get_logger

logger = get_logger(__name__)


class FileRouterRepository(IFileRouterRepository):
    """
    PostgreSQL implementation of FileRouter repository using SQLAlchemy ORM.
    Handles database operations related to file routing and extraction data.
    """

    def get_multiple_entities_or_investor(
        self,
        db: Session,
        file_uid: UUID
    ) -> List[ExtractFile]:
        """
        Retrieve a list of ExtractFile entities associated with a specific document UID.
        Replicates the logic of the 'GetMultipleEntitiesORInvestor' stored procedure.

        Args:
            db (Session): The database session.
            file_uid (UUID): The unique identifier of the document (file).

        Returns:
            List[ExtractFile]: A list of matching ExtractFile entities.

        Raises:
            Exception: If an error occurs during the database query.
        """
        try:
            logger.info(f"Fetching ExtractFile records for file_uid: {file_uid}")

            results = db.query(ExtractFile).filter(
                ExtractFile.fileuid == file_uid
            ).all()

            logger.info(f"Successfully fetched {len(results)} ExtractFile records for file_uid: {file_uid}")
            return results
        except Exception as ex:
            logger.error(f"Error fetching ExtractFile records for file_uid {file_uid}: {ex}", exc_info=True)
            raise
