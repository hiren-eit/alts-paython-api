from typing import List, Any, Dict
from sqlalchemy.orm import Session
from uuid import UUID


class IFileRouterRepository:
    """Repository interface for FileRouter"""

    def get_multiple_entities_or_investor(
        self,
        db: Session,
        file_uid: UUID
    ) -> List[Any]:
        """
        Returns list of extract files by file_uid.
        Replicates GetMultipleEntitiesORInvestor logic.
        """
        raise NotImplementedError
