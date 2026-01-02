from src.utils.helper import serialize_orm
from src.domain.entities.master_configuration_type import MasterConfigurationType
from src.domain.services.master_configuration_type_service import (
    MasterConfigurationTypeService,
)
from src.domain.dtos.response_object import ResponseObject
from uuid import UUID
from src.domain.dtos.file_account_validation_dto import FileAccountValidation
from src.domain.services.file_account_validation_service import (
    FileAccountValidationService,
)
from typing import List
from importlib import import_module
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.core.settings import get_connection_config
from src.domain.dtos.file_activity_dto import FileActivity
from src.infrastructure.logging.logger_manager import get_logger
from src.infrastructure.database.connection_manager import get_db
from fastapi import status

# Dynamic Repository Import
DATABASE_URL, active_repository_path = get_connection_config()
masterConfigurationRepository = import_module(
    f"{active_repository_path}.master_configuration_type_repository"
).MasterConfigurationTypeRepository

router = APIRouter(prefix="/master-configuration", tags=["MasterConfiguration"])
logger = get_logger(__name__)


# Dependency Injection
def get_service(db: Session = Depends(get_db)) -> MasterConfigurationTypeService:
    repository = masterConfigurationRepository()
    return MasterConfigurationTypeService(repository)


@router.get(
    "/master-configuration-type",
    response_model=ResponseObject,
)
def get_master_configuration_type(
    type: str = Query(..., description="Type"),
    service: MasterConfigurationTypeService = Depends(get_service),
    db: Session = Depends(get_db),
):
    """
    Get master configuration by type.
    """
    logger.info("master-configuration-type called: type=%s", type)

    try:
        data = service.get_master_configuration_type(db, type)
        data_dicts = serialize_orm(data)
        return ResponseObject(
            result_code=str(status.HTTP_200_OK),
            count=len(data),
            result_object=data_dicts,
            result_message="Success",
        )

    except Exception as ex:
        logger.error(
            "Error retrieving master configuration type",
            exc_info=True,
        )

        return ResponseObject(
            result_code=str(status.HTTP_500_INTERNAL_SERVER_ERROR),
            count=0,
            in_review_count=0,
            result_object=None,
            result_message=str(ex),
        )
