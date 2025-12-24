from importlib import import_module
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.domain.services.file_operation_service import FileOperationService
from src.domain.dtos.document_receiver_dto import DocumentRequestModel
from src.domain.dtos.master_dto import ResponseObjectModel
from src.core.settings import get_connection_config
from src.infrastructure.database.connection_manager import get_db
from src.infrastructure.logging.logger_manager import get_logger

DATABASE_URL, active_repository_path = get_connection_config()
FileServiceRepository = import_module(f"{active_repository_path}.file_service_repository").FileServiceRepository

logger = get_logger(__name__)
router = APIRouter(prefix="/file-service", tags=["FileService"])

repository = FileServiceRepository()
service = FileOperationService(repository)

@router.post("/document-retrieval", response_model=ResponseObjectModel)
def document_retrieval(
    documents: DocumentRequestModel,
    db: Session = Depends(get_db)
):
    """
    API to upload file.
    This endpoint replicates the /DocumentRetrieval API from .NET
    """
    return service.document_retrieval(db, documents)