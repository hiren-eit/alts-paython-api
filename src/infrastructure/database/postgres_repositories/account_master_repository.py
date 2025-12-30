from typing import List
from uuid import UUID
from sqlalchemy.orm import Session

from src.domain.interfaces.account_master_repository_interface import IAccountMasterRepository
from src.infrastructure.database.query_builders.get_account_data_by_file_uid_query_builder import GetAccountDataByFileUID
from src.domain.dtos.account_file_data_dto import AccountFileDataResponse
from src.infrastructure.logging.logger_manager import get_logger

logger = get_logger(__name__)

class AccountMasterRepository(IAccountMasterRepository):
    """PostgreSQL implementation of AccountMaster repository"""

    def get_account_data_by_file_uid(self, db: Session, file_uid: UUID) -> List[AccountFileDataResponse]:
        """
        Skeleton implementation for GetAccountDataByFileUid.
        """
        try:
            logger.info(f"Postgres: GetAccountDataByFileUid called for {file_uid}")
            # Return empty list as skeleton
            query_builder = GetAccountDataByFileUID(db, file_uid)
            result = query_builder.get_account_data_by_fileuid()
            return result
        except Exception as ex:
            logger.error(f"Postgres: GetAccountDataByFileUid error: {ex}", exc_info=True)
            db.rollback()
            raise
