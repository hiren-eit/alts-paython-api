from importlib import import_module
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.core.settings import get_connection_config
from src.domain.services.file_configuration_service import FileConfigurationService
from src.domain.dtos.file_configuration_dto import FileConfigurationResponse, FileConfiguration
from src.infrastructure.database.connection_manager import get_db
from src.infrastructure.logging.logger_manager import get_logger
from uuid import UUID

DATABASE_URL, active_repository_path = get_connection_config()
FileConfigurationRepository = import_module(f"{active_repository_path}.file_configuration_repository").FileConfigurationRepository

logger = get_logger(__name__)
router = APIRouter(prefix="/files", tags=["FileConfiguration"])

repository = FileConfigurationRepository()
service = FileConfigurationService(repository)

@router.get("/get-all-active-file-configuration-list", response_model=FileConfigurationResponse)
def get_all_active_file_configuration_list(
    db: Session = Depends(get_db)
):
    """
    Returns all active file configuration list with total count.

    Returns:
                dict: {
                    "result_code": "SUCCESS",
                    "total": int,
                    "data": List[FileConfiguration]
                }
    """
    return service.get_all_active_file_configuration_list(db)


@router.post("/add-file-configuration", response_model=bool)
async def save_file_configuration(
    fileConfiguration: FileConfiguration,
    db: Session = Depends(get_db),
):
    """
        Add file configuration.
        Replicates the AddFileConfiguration stored procedure logic.
    """
    return await service.save_file_configuration(db, fileConfiguration)


@router.post("/update-file-configuration", response_model=bool)
async def update_file_configuration(
    fileConfiguration: FileConfiguration,
    db: Session = Depends(get_db),
):
    """
        Update file configuration.
        Replicates the UpdateFileConfiguration stored procedure logic.
    """
    return await service.update_file_configuration(db, fileConfiguration)


@router.post("/update-file-configuration-action", response_model=bool)
async def update_file_action_configuration(
    fileConfiguration: FileConfiguration,
    db: Session = Depends(get_db),
):
    """
        Update file configuration action.
        Replicates the UpdateFileConfigurationAction stored procedure logic.
    """
    return await service.update_file_action_configuration(db, fileConfiguration)


@router.get("/get-file-configuration-by-id", response_model=FileConfigurationResponse)
def get_file_configuration_by_id(
    fileconfigurationid: int,
    db: Session = Depends(get_db), 
):
    """
        Returns file file by id.
        Replicates the GetDocumentConfigurationByID stored procedure logic.

        Returns:
                dict: {
                    "result_code": "SUCCESS",
                    "total": int,
                    "data": List[FileConfiguration]
                } 
    """
    return service.get_file_configuration_by_id(db, fileconfigurationid)


@router.get("/get-file-configuration-type", response_model=FileConfigurationResponse)
def get_file_configuration_type(
    db: Session = Depends(get_db)
):
    """
        Returns file configuration type.
        Replicates the GetFileConfigurationType stored procedure logic.
        
        Returns:
                dict: {
                    "result_code": "SUCCESS",
                    "total": int,
                    "data": List[FileConfiguration]
                }
    """
    return service.get_file_configuration_type(db)


@router.get("/get-file-configuration-by-schema-type", response_model=FileConfigurationResponse)
def get_file_configuration_by_schema_type(
    schematype: str,
    db: Session = Depends(get_db)
):
    """
        Returns file configuration by schema type.
        Replicates the GetDocumentConfigurationBySchemaType stored procedure logic.
        
        Returns:
                dict: {
                    "result_code": "SUCCESS",
                    "total": int,
                    "data": List[FileConfiguration]
                }
    """
    return service.get_file_configuration_by_schema_type(db, schematype)