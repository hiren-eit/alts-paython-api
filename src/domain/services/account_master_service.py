from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from src.domain.interfaces.account_master_repository_interface import IAccountMasterRepository
from src.domain.dtos.account_file_data_dto import AccountDocumentDataResponse

class AccountMasterService:
    def __init__(self, repository: IAccountMasterRepository):
        self.repo = repository

    def get_account_data_by_file_uid(self, db: Session, file_uid: UUID) -> List[AccountDocumentDataResponse]:
        """
        Get account data by file_uid.
        """
        return self.repo.get_account_data_by_file_uid(db, file_uid)
