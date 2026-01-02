from src.domain.dtos.file_manager_dto import ReplayFileRequestDTO
from src.domain.dtos.response_object import ResponseObject
from src.domain.dtos.file_request_dto import FileRequestDTO
from src.infrastructure.database.postgres_repositories.file_manager_repository import (
    FileManagerRepository,
)
from importlib import import_module
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.core.settings import get_connection_config
from src.domain.services.file_manager_service import FileManagerService
from src.domain.dtos.file_manager_dto import (
    FileManagerFilter,
    FileManagerResponse,
    IgnoreFilesRequest,
    ApproveFileRequest,
)
from src.domain.dtos.extract_file_dto import ExtractFile
from src.domain.dtos.file_comment_dto import AddFileCommentRequest
from src.domain.dtos.update_extract_file_dto import (
    UpdateExtractFileRequest,
    ResponseObjectModel,
)
from src.domain.dtos.file_details_dto import FileDetailsResponse
from src.infrastructure.database.connection_manager import get_db
from src.infrastructure.logging.logger_manager import get_logger
from uuid import UUID
from typing import Dict, List

logger = get_logger(__name__)
router = APIRouter(prefix="/files", tags=["FileManager"])


def get_file_manager_service(db: Session = Depends(get_db)) -> FileManagerService:
    """
    Dependency provider for FileManagerService.
    Dynamically loads the repository based on the active connection configuration.
    """
    try:
        _, active_repository_path = get_connection_config()
        module_path = f"{active_repository_path}.file_manager_repository"
        repository_module = import_module(module_path)
        repository_cls = getattr(repository_module, "FileManagerRepository")

        repository = repository_cls()
        return FileManagerService(repository)
    except (ImportError, AttributeError) as e:
        logger.critical(f"Failed to load FileManagerRepository: {e}", exc_info=True)
        raise RuntimeError("Configuration error: Repository could not be loaded.")


@router.post("/get-file-manager", response_model=FileManagerResponse)
def get_file_manager_list(
    filters: FileManagerFilter,
    service: FileManagerService = Depends(get_file_manager_service),
    db: Session = Depends(get_db),
):
    """
    Get paginated file manager list with filters.

    This endpoint replicates the GetFileManager stored procedure,
    providing the same filtering, sorting, and pagination capabilities
    using SQLAlchemy ORM queries that work on both PostgreSQL and SQL Server.

    Supported filters:
    - filetype: file type (e.g., "All", specific type)
    - file_status: Tab filter (ToReview, Approved, Completed, etc.)
    - sla_type: SLA status (All, withinsla, onsla, slabreached, uncategorized)
    - search_text: Search in filename, fileuid, email subject, etc.
    - Date filters, file type filters, and many more

    Returns paginated results with account info and SLA calculations.
    """
    logger.info(
        f"GetFileManagerListApi called: status={filters.file_status}, page={filters.page_number}"
    )
    return service.get_file_manager_list(db, filters)


@router.post("/get-file-details-by-fileuid", response_model=FileDetailsResponse)
def get_file_details_by_fileuid(
    fileuid: UUID,
    service: FileManagerService = Depends(get_file_manager_service),
    db: Session = Depends(get_db),
):
    """
    Get file details by fileuid.

    This endpoint replicates the GetFileDetailsByFileUID stored procedure,
    providing the same functionality using SQLAlchemy ORM queries that work on
    both PostgreSQL and SQL Server.
    """
    logger.info(f"GetFileDetailsByFileUID called: fileuid={str(fileuid)}")
    # Updated method name
    return service.get_file_details_by_file_uid(db, fileuid)


@router.post("/get-manual-extraction-config_fields-by-id")
def get_manual_extraction_config_fields_by_id(
    fileConfigurationId: int,
    service: FileManagerService = Depends(get_file_manager_service),
    db: Session = Depends(get_db),
):
    """
    Get manual extraction config fields by id.

    This endpoint replicates the GetManualExtractionConfigFieldsById stored procedure,
    providing the same functionality using SQLAlchemy ORM queries that work on
    both PostgreSQL and SQL Server.
    """
    logger.info(f"GetManualExtractionConfigFieldsById called: id={fileConfigurationId}")
    return service.get_manual_extraction_config_fields_by_id(db, fileConfigurationId)


@router.post("/get-extract-file-api", response_model=None)
def get_extract_file_api(
    fileuid: UUID,
    service: FileManagerService = Depends(get_file_manager_service),
    db: Session = Depends(get_db),
):
    """
    Get extraction file details by fileuid.

    This endpoint retrieves comprehensive extraction file information including:
    - Extraction file details (classification, extraction data, etc.)
    - File configuration fields associated with the classification
    - Object-type fields from the configuration
    - Security mappings for specific classifications (Rage, BrokerageMSBilling)
    - Update file references

    Returns:
        ExtractionFileField with all related data
    """
    logger.info(f"GetExtractFileApi called: fileuid={fileuid}")
    return service.get_extract_file_api(db, fileuid)


@router.get("/get-extract-files-by-fileuid-async", response_model=List[ExtractFile])
def get_extract_files_by_file_uid(
    fileuid: UUID,
    service: FileManagerService = Depends(get_file_manager_service),
    db: Session = Depends(get_db),
):
    """
    Get extract files by fileuid.
    """
    logger.info(f"GetExtractFilesByFileUIDAsync called: fileuid={fileuid}")
    # Updated method name
    return service.get_extract_files_by_file_uid(db, fileuid)


# @router.post("/add-file-comment")
# def add_file_comment(
#     request: AddFileCommentRequest,
#     service: FileManagerService = Depends(get_file_manager_service),
#     db: Session = Depends(get_db),
# ):
#     """
#     Add a comment to a file.
#     """
#     logger.info(f"AddFileComment called: fileuid={request.fileuid}")
#     result = service.add_file_comment(
#         db, request.fileuid, request.comment, request.createdby
#     )
#     if result:
#         return True
#     from fastapi import HTTPException

#     raise HTTPException(
#         status_code=500, detail="An error occurred while adding the file comment."
#     )


@router.post("/update-extract-file-api", response_model=ResponseObjectModel)
def update_extract_file(
    request: UpdateExtractFileRequest,
    service: FileManagerService = Depends(get_file_manager_service),
    db: Session = Depends(get_db),
):
    repo = FileManagerRepository()

    extract_file_detail = repo.get_active_extraction_file_detail(
        db, request.extraction_file_detail.fileuid
    )
    file_manager = repo.get_file_manager_by_fileuid(
        db, request.extraction_file_detail.fileuid
    )

    return service.update_extract_file(
        db,
        extract_file_detail=extract_file_detail,
        file_manager=file_manager,
        request=request,
    )


@router.post("/files-start-processing", response_model=ResponseObject)
def file_retrieval(
    request: FileRequestDTO,
    service: FileManagerService = Depends(get_file_manager_service),
    db: Session = Depends(get_db),
):

    return service.file_retrieval(
        db,
        request=request,
    )


@router.post("/replay_files", response_model=ResponseObject)
async def replay_files(
    request: ReplayFileRequestDTO,
    service: FileManagerService = Depends(get_file_manager_service),
    db: Session = Depends(get_db),
):
    processed_count = await service.replay_files(
        db, request.fileuids, request.comment, request.updatedby
    )
    success = processed_count > 0
    return ResponseObject(
        result_code="200" if success else "500",
        result_message=(
            f"{processed_count} files replayed" if success else "No files processed"
        ),
        count=processed_count,
        result_object=None,
    )


@router.post("/update-file-status-api")
async def update_file_status_api(
    request: IgnoreFilesRequest,
    service: FileManagerService = Depends(get_file_manager_service),
    db: Session = Depends(get_db),
):
    """
    Update file status API.
    """
    return await service.update_file_status(db, request)


# @router.post("/approve-file", response_model=ResponseObjectModel)
# async def approve_file(
#     request: ApproveFileRequest,
#     service: FileManagerService = Depends(get_file_manager_service),
#     db: Session = Depends(get_db),
# ):
#     """
#     Approve a file for ingestion.
#     """
#     logger.info(f"ApproveFile called: fileuid={request.fileUid}")
#     return await service.approve_file(db, request)
