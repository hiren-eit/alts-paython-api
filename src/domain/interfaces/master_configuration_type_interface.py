from src.domain.entities.master_configuration_type import MasterConfigurationType
from abc import ABC, abstractmethod
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session


class IMasterConfigurationTypeRepository(ABC):
    """Interface for FileActivity Repository"""

    @abstractmethod
    def get_master_configuration_type(
        self, db: Session, type: str
    ) -> List[MasterConfigurationType]:
        """
        Get file account details by fileuid.
        """
        pass
