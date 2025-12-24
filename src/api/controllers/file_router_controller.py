from typing import List, Any
from importlib import import_module
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.core.settings import get_connection_config
from src.domain.services.file_router_service import FileRouterService
from src.domain.dtos.extract_file_dto import ExtractDocument
from src.infrastructure.database.connection_manager import get_db
from src.infrastructure.logging.logger_manager import get_logger
from src.api.controllers.base_controller import BaseController

# Initialize Logger
logger = get_logger(__name__)

# Initialize Router
router = APIRouter(prefix="/file-router", tags=["FileRouter"])


def get_file_router_service(db: Session = Depends(get_db)) -> FileRouterService:
    """
    Dependency provider for FileRouterService.
    Dynamically loads the repository based on the active connection configuration.
    """
    try:
        _, active_repository_path = get_connection_config()
        module_path = f"{active_repository_path}.file_router_repository"
        repository_module = import_module(module_path)
        repository_cls = getattr(repository_module, "FileRouterRepository")
        
        repository = repository_cls()
        return FileRouterService(repository)
    except (ImportError, AttributeError) as e:
        logger.critical(f"Failed to load FileRouterRepository: {e}", exc_info=True)
        raise RuntimeError("Configuration error: Repository could not be loaded.")


class FileRouterController(BaseController):
    """
    Controller for File Routing operations.
    """

    @router.get("/extraction-data", response_model=List[ExtractDocument], summary="Get Extraction Data by Document UID")
    def get_extraction_data(
        file_uid: UUID = Query(..., alias="DocUID", description="The distinct file identifier (FileUID)"),
        service: FileRouterService = Depends(get_file_router_service),
        db: Session = Depends(get_db)
    ):
        """
        Retrieve multiple entities or investor extraction data for a given document (file).
        Returns an empty list if an error occurs.
        """
        try:
            logger.info(f"Request received to fetch extraction data for FileUID: {file_uid}")
            result = service.get_multiple_entities_or_investor(db, file_uid)
            return result
        except Exception as ex:
            logger.error(f"Error in get_extraction_data for FileUID {file_uid}: {ex}", exc_info=True)
            # Preserving original behavior: return empty list on error
            return []
