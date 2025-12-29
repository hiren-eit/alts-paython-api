from typing import List
from uuid import UUID
from sqlalchemy.orm import Session

from src.domain.interfaces.account_master_repository_interface import IAccountMasterRepository
from src.domain.dtos.account_file_data_dto import AccountFileDataResponse
from src.infrastructure.logging.logger_manager import get_logger

logger = get_logger(__name__)

class AccountMasterRepository(IAccountMasterRepository):
    """SQL Server implementation of AccountMaster repository"""

    def get_account_data_by_file_uid(self, db: Session, file_uid: UUID) -> List[AccountFileDataResponse]:
        """
        Skeleton implementation for GetAccountDataByFileUid.
        """
        try:
            logger.info(f"SQL Server: GetAccountDataByFileUid called for {file_uid}")
            # Return empty list as skeleton
            return []
        except Exception as ex:
            logger.error(f"SQL Server: GetAccountDataByFileUid error: {ex}", exc_info=True)
            raise
