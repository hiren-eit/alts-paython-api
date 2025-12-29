from abc import ABC, abstractmethod
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from src.domain.dtos.account_file_data_dto import AccountFileDataResponse

class IAccountMasterRepository(ABC):
    """Interface for AccountMaster Repository"""
    
    @abstractmethod
    def get_account_data_by_file_uid(self, db: Session, file_uid: UUID) -> List[AccountFileDataResponse]:
        """
        Get account data by file_uid.
        Replicates GetAccountDataByDocUID stored procedure logic.
        """
        pass
