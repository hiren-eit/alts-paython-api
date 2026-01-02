from src.domain.entities.master_configuration_type import MasterConfigurationType
from src.domain.interfaces.master_configuration_type_interface import (
    IMasterConfigurationTypeRepository,
)
from src.domain.dtos.file_account_validation_dto import FileAccountValidation
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session


class MasterConfigurationTypeService:
    def __init__(self, repository: IMasterConfigurationTypeRepository):
        self.repo = repository

    def get_master_configuration_type(
        self,
        db: Session,
        type: str,
    ) -> List[MasterConfigurationType]:
        return self.repo.get_master_configuration_type(db, type)
