from abc import ABC, abstractmethod
from typing import List
from sqlalchemy.orm import Session
from src.domain.dtos.account_details_dto import PublishingRecordsResultResponse, PublishingQueryParamsInput

class IAccountDetailsRepository(ABC):
    """Interface for AccountDetails Repository"""
    
    @abstractmethod
    def get_publishing_records(self, db: Session, parameters: PublishingQueryParamsInput) -> List[PublishingRecordsResultResponse]:
        """
        Returns file file by id.
        Replicates the GetPublishingRecords stored procedure logic.
        """
        pass
