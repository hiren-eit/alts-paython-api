from typing import List, Any
from importlib import import_module
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from src.core.settings import get_connection_config
from src.domain.services.account_details_service import AccountDetailsService
from src.domain.dtos.account_details_dto import PublishingRecordsResultResponse
from src.infrastructure.logging.logger_manager import get_logger
from src.infrastructure.database.connection_manager import get_db
from src.domain.dtos.account_details_dto import PublishingQueryParamsInput, PublishingRecordsResultResponse

# Initialize Logger
logger = get_logger(__name__)

# Initialize Router
router = APIRouter(prefix="/account-details", tags=["AccountDetails"])

# Dependency Injection
def get_service(db: Session = Depends(get_db)) -> AccountDetailsService:
    try:
        _, active_repository_path = get_connection_config()
        module_path = f"{active_repository_path}.account_details_repository"
        repository_module = import_module(module_path)
        repository_cls = getattr(repository_module, "AccountDetailsRepository")
        
        repository = repository_cls()
        return AccountDetailsService(repository)
    except (ImportError, AttributeError) as e:
        logger.critical(f"Failed to load FileManagerRepository: {e}", exc_info=True)
        raise RuntimeError("Configuration error: Repository could not be loaded.")

@router.post("/get-publishing-records", response_model=List[PublishingRecordsResultResponse])
def get_publishing_records(parameters: PublishingQueryParamsInput, service: AccountDetailsService = Depends(dependency=get_service), db: Session = Depends(dependency=get_db)):
    """
        Returns file file by id.
        Replicates the GetPublishingRecords stored procedure logic.

        Returns:
                List[FileConfiguration]
    """
    return service.get_publishing_records(db, parameters)