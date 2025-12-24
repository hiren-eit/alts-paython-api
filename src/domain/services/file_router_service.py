from sqlalchemy.orm import Session
from src.domain.interfaces.file_router_repository_interface import IFileRouterRepository
from uuid import UUID


class FileRouterService:
    def __init__(self, repository: IFileRouterRepository):
        self.repo = repository

    def get_multiple_entities_or_investor(self, db: Session, file_uid: UUID):
        """
        Get extract documents by file_uid.
        Replicates GetMultipleEntitiesORInvestor logic.
        """
        return self.repo.get_multiple_entities_or_investor(db, file_uid)
