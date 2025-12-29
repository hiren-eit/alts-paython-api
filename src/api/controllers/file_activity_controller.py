from typing import List
from importlib import import_module
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from src.core.settings import get_connection_config
from src.domain.services.file_activity_service import FileActivityService
from src.domain.dtos.file_activity_dto import FileActivity
from src.infrastructure.logging.logger_manager import get_logger
from src.infrastructure.database.connection_manager import get_db

# Dynamic Repository Import
DATABASE_URL, active_repository_path = get_connection_config()
FileActivityRepository = import_module(f"{active_repository_path}.file_activity_repository").FileActivityRepository

router = APIRouter(prefix="/files/activity", tags=["FileActivity"])
logger = get_logger(__name__)

# Dependency Injection
def get_service(db: Session = Depends(get_db)) -> FileActivityService:
    repository = FileActivityRepository()
    return FileActivityService(repository)

@router.get("/get-file-activity-log-api", response_model=List[FileActivity])
def get_file_activity_logs(
    docuid: UUID = Query(..., description="File UID"),
    service: FileActivityService = Depends(get_service),
    db: Session = Depends(get_db)
):
    """
    Get file activity logs by fileuid.
    Renamed from GetFileActivityLogApi as per requirements.
    """
    logger.info(f"GetFileActivityLogApi called: docuid={docuid}")
    
    result = service.get_file_activity_logs(db, docuid)
    
    if not result:
        return []
        
    return result
