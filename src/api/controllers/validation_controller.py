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

# Dynamic Repository Import
DATABASE_URL, active_repository_path = get_connection_config()
ValidationRepository = import_module(
    f"{active_repository_path}.file_account_validation_repository"
).FileAccountvalidationRepository

router = APIRouter(prefix="/files/validation", tags=["validation"])
logger = get_logger(__name__)


# Dependency Injection
def get_service(db: Session = Depends(get_db)) -> FileAccountValidationService:
    repository = ValidationRepository()
    return FileAccountValidationService(repository)


@router.get("/file-account-details", response_model=List[FileAccountValidation])
def get_file_account_details(
    fileuid: UUID = Query(..., description="File UID"),
    service: FileAccountValidationService = Depends(get_service),
    db: Session = Depends(get_db),
):
    """
    Get file account details by fileuid.
    """
    logger.info(f"GetFileAccountDetailsApi called: fileuid={fileuid}")

    result = service.get_file_account_details(db, fileuid)

    if not result:
        return []

    return result
