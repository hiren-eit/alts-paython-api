from sqlalchemy.orm import Session
from src.domain.interfaces.file_router_repository_interface import IFileRouterRepository
from src.domain.dtos.resolve_file_update_dto import ResolveFileUpdate
from uuid import UUID
from typing import Dict


class FileRouterService:
    def __init__(self, repository: IFileRouterRepository):
        self.repo = repository

    def get_multiple_entities_or_investor(self, db: Session, file_uid: UUID):
        """
        Get extract files by file_uid.
        Replicates GetMultipleEntitiesORInvestor logic.
        """
        return self.repo.get_multiple_entities_or_investor(db, file_uid)
    
    def resolve_file_update(
        self,
        db: Session,
        resolveUpdate: ResolveFileUpdate,
    ) -> Dict:
        """
        Resolves file updates
        """
        return self.repo.resolve_file_update(db, resolveUpdate)
