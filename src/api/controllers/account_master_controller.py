from typing import List, Any
from importlib import import_module
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from src.core.settings import get_connection_config
from src.domain.services.account_master_service import AccountMasterService
from src.domain.dtos.account_file_data_dto import AccountDocumentDataResponse
from src.infrastructure.logging.logger_manager import get_logger
from src.infrastructure.database.connection_manager import get_db
from src.api.controllers.base_controller import BaseController

# Initialize Logger
logger = get_logger(__name__)

# Initialize Router
router = APIRouter(prefix="/account-master", tags=["AccountMaster"])


def get_account_master_service(db: Session = Depends(get_db)) -> AccountMasterService:
    """
    Dependency provider for AccountMasterService.
    Dynamically loads the repository based on the active connection configuration.
    """
    try:
        _, active_repository_path = get_connection_config()
        module_path = f"{active_repository_path}.account_master_repository"
        repository_module = import_module(module_path)
        repository_cls = getattr(repository_module, "AccountMasterRepository")
        
        repository = repository_cls()
        return AccountMasterService(repository)
    except (ImportError, AttributeError) as e:
        logger.critical(f"Failed to load AccountMasterRepository: {e}", exc_info=True)
        raise RuntimeError("Configuration error: Repository could not be loaded.")


class AccountMasterController(BaseController):
    """
    Controller for Account Master operations.
    """

    @router.get("/document-data", response_model=List[AccountDocumentDataResponse], summary="Get Account Data by Document UID")
    def get_account_data_by_docuid(
        file_uid: UUID = Query(..., alias="docUID", description="The unique identifier of the file (FileUID)"),
        service: AccountMasterService = Depends(get_account_master_service),
        db: Session = Depends(get_db)
    ):
        """
        Retrieve account data associated with a specific file UID.
        """
        logger.info(f"Request received to fetch account data for FileUID: {file_uid}")
        
        def _execute():
            # Uses updated service method name: get_account_data_by_file_uid
            result = service.get_account_data_by_file_uid(db, file_uid)
            if not result:
                logger.warning(f"No account data found for FileUID: {file_uid}")
                raise HTTPException(status_code=404, detail="Not found")
            return result

        return BaseController.safe_execute(_execute)
