from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from src.domain.interfaces.account_details_repository_interface import IAccountDetailsRepository
from src.domain.dtos.account_details_dto import PublishingQueryParamsInput, PublishingRecordsResultResponse

class AccountDetailsService:
    def __init__(self, repository: IAccountDetailsRepository):
        self.repo = repository

    def get_publishing_records(self, db: Session, parameters: PublishingQueryParamsInput) -> List[PublishingRecordsResultResponse]:
        """
        Returns file file by id.
        Replicates the GetPublishingRecords stored procedure logic.
        """
        return self.repo.get_publishing_records(db, parameters)