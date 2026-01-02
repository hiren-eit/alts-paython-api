"""
PostgreSQL File Manager Repository
Clean implementation using separated query builder and result enricher.
"""

from typing import Optional
from datetime import datetime
from src.domain.dtos.file_request_dto import FileRequestDTO
from src.domain.entities.file_manager import FileManager
from src.domain.entities.extraction_file_detail import ExtractionFileDetail
from typing import List, Any, Dict

from sqlalchemy.orm import Session

from src.domain.dtos.extract_file_dto import FileSecurityMappingDTO
from src.domain.interfaces.file_manager_repository_interface import (
    IFileManagerRepository,
)
from src.domain.dtos.file_manager_dto import FileManagerFilter
from src.domain.dtos.update_extract_file_dto import (
    UpdateExtractFileRequest,
    ResponseObjectModel,
)
from src.infrastructure.database.query_builders import (
    FileManagerQueryBuilder,
    FileManagerResultEnricher,
)
from src.infrastructure.database.query_builders.file_details_query_builder import (
    FileDetailsQueryBuilder,
)
from src.infrastructure.database.query_builders.file_details_result_enricher import (
    FileDetailsResultEnricher,
)
from src.infrastructure.logging.logger_manager import get_logger
from src.domain.dtos.file_details_dto import FileDetailsResponse
from uuid import UUID
from src.domain.dtos.extract_file_dto import (
    ExtractionFileField,
    ExtractionFileDetailDTO,
    FileConfigurationFieldDTO,
    FileSecurityMappingDTO,
)
from src.domain.entities.file_process_log import FileProcessLog
from src.domain.entities.file_activity import FileActivity
from src.domain.entities.file_manager import FileManager

logger = get_logger(__name__)


class FileManagerRepository(IFileManagerRepository):
    """PostgreSQL implementation of FileManager repository using SQLAlchemy ORM"""

    def get_file_manager_list(self, db: Session, filters: FileManagerFilter) -> Dict:
        """
        Replicates GetFileManagerList stored procedure logic.
        Uses separated QueryBuilder and ResultEnricher for clean code.
        """
        try:
            logger.info(
                f"GetFileManagerList: status={filters.file_status}, fileType={filters.file_type}"
            )

            # Build query with all filters
            query_builder = FileManagerQueryBuilder(db, filters)
            query_builder.build_query()

            # Get count and results
            total_count = query_builder.get_count()
            results = query_builder.get_results()

            # Enrich results with account info and SLA calculations
            enricher = FileManagerResultEnricher(db, filters)
            items = enricher.enrich(results)

            logger.info(
                f"GetFileManagerList: returned {len(items)} items, total={total_count}"
            )

            return {
                "total": total_count,
                "page": filters.page_number,
                "page_size": filters.page_size,
                "data": items,
            }

        except Exception as ex:
            logger.error(f"GetFileManagerList error: {ex}", exc_info=True)
            raise

    def get_file_details_by_file_uid(
        self, db: Session, fileuid: UUID
    ) -> FileDetailsResponse:
        """
        Replicates GetFileDetailsByFileUID stored procedure logic.
        Uses separated QueryBuilder and ResultEnricher for clean code.
        """
        try:
            logger.info(f"GetFileDetailsByFileUID: fileuid={fileuid}")

            # 1. Build query
            query_builder = FileDetailsQueryBuilder(db, str(fileuid))
            query_builder.build_query()

            # 2. Fetch raw DB record (single row)
            result = query_builder.get_one()

            if not result:
                logger.info(f"GetFileDetailsByFileUID: No file found for {fileuid}")
                return {"total": 0, "data": []}

            # 3. Enrich result
            enricher = FileDetailsResultEnricher(db)
            enriched = enricher.enrich(result)

            logger.info(f"GetFileDetailsByFileUID: returning details for {fileuid}")

            # Wrap in paginated structure to match likely API requirements
            return {"total": 1, "data": [enriched]}

        except Exception as ex:
            logger.error(f"GetFileDetailsByFileUID error: {ex}", exc_info=True)
            raise

    def get_manual_extraction_config_fields_by_id(
        self, db: Session, fileConfigurationId: int
    ):
        """
        Replicates GetManualExtractionConfigFieldsById stored procedure logic.
        Queries configuration and its associated 'Object' type fields.
        """
        try:
            from src.domain.entities.file_configuration import FileConfiguration
            from src.domain.entities.file_configuration_field import (
                FileConfigurationField,
            )

            logger.info(
                f"GetManualExtractionConfigFieldsById: id={fileConfigurationId}"
            )

            # 1. Verify Configuration exists and is active
            config = (
                db.query(FileConfiguration)
                .filter(
                    FileConfiguration.fileid == fileConfigurationId,
                    FileConfiguration.isactive == True,
                )
                .first()
            )

            if not config:
                logger.warning(
                    f"GetManualExtractionConfigFieldsById: Configuration {fileConfigurationId} not found or inactive"
                )
                return {"count": 0, "resultobject": [], "resultcode": "NOT_FOUND"}

            # 2. Get Fields where DataType is 'Object'
            fields = (
                db.query(FileConfigurationField)
                .filter(
                    FileConfigurationField.fileconfigurationid == fileConfigurationId,
                    FileConfigurationField.isactive == True,
                    FileConfigurationField.datatype == "Object",
                )
                .all()
            )

            # Map to DTO-like list for response
            result_list = []
            for f in fields:
                result_list.append(
                    {
                        "fileconfigurationfieldid": f.fileconfigurationfieldid,
                        "fileconfigurationid": f.fileconfigurationid,
                        "name": f.name,
                        "datatype": f.datatype,
                        "isactive": f.isactive,
                    }
                )

            return {
                "count": len(result_list),
                "resultobject": result_list,
                "resultcode": "SUCCESS",
            }

        except Exception as ex:
            logger.error(
                f"GetManualExtractionConfigFieldsById error: {ex}", exc_info=True
            )
            raise

    def get_extract_file_api(self, db: Session, fileuid: UUID) -> Dict:
        """
        get the extraction file details for the given file uid
        """
        try:
            from src.domain.entities.extraction_file_detail import ExtractionFileDetail
            from src.domain.entities.file_configuration import FileConfiguration
            from src.domain.entities.file_configuration_field import (
                FileConfigurationField,
            )

            logger.info(f"GetExtractFileApi: fileuid={fileuid}")

            extraction_file_field = ExtractionFileField()

            # 1. Get active ExtractionFileDetail
            item = (
                db.query(ExtractionFileDetail)
                .filter(
                    ExtractionFileDetail.fileuid == fileuid,
                    ExtractionFileDetail.isactive == True,
                )
                .first()
            )

            if item:
                extraction_file_field.extraction_file_detail = (
                    ExtractionFileDetailDTO.model_validate(item)
                )

                # 2. Configuration logic
                if item.classification and item.classification.strip():
                    file_configuration = (
                        db.query(FileConfiguration)
                        .filter(
                            FileConfiguration.configurationname == item.classification,
                            FileConfiguration.isactive == True,
                        )
                        .first()
                    )

                    if file_configuration:
                        extraction_file_field.configuration_id = (
                            file_configuration.fileconfigurationid
                        )

                        # 3. Get all active configuration fields
                        file_configuration_fields = (
                            db.query(FileConfigurationField)
                            .filter(
                                FileConfigurationField.fileconfigurationid
                                == file_configuration.fileconfigurationid,
                                FileConfigurationField.isactive == True,
                            )
                            .all()
                        )

                        if file_configuration_fields:
                            extraction_file_field.file_configuration_fields = [
                                FileConfigurationFieldDTO.model_validate(f)
                                for f in file_configuration_fields
                            ]

                            # 4. Object datatype fields
                            object_fields = [
                                f
                                for f in file_configuration_fields
                                if f.datatype == "Object"
                            ]

                            if object_fields:
                                extraction_file_field.object_fields = [
                                    FileConfigurationFieldDTO.model_validate(f)
                                    for f in object_fields
                                ]

                    # 5. Security mappings (always assign when classification matches)
                    if item.classification in ("Rage", "BrokerageMSBilling"):
                        extraction_file_field.file_security_mappings = (
                            self._get_file_security_by_fileuid(db, fileuid) or []
                        )

                # 6. Update file lookup (matches .NET behavior)
                update_file = (
                    db.query(ExtractionFileDetail.fileuid)
                    .filter(
                        ExtractionFileDetail.isactive == True,
                        ExtractionFileDetail.update_file_id == fileuid,
                    )
                    .first()
                )

                if update_file and update_file[0]:
                    extraction_file_field.update_file_id = str(update_file[0])

            logger.info("DATABASE: Retrieved Extraction file details.")
            return extraction_file_field.model_dump()

        except Exception as ex:
            logger.error(
                "DATABASE: Error occurred while getting file details.", exc_info=True
            )
            raise Exception(
                "An error occurred while retrieving data from the database."
            ) from ex

    def _get_file_security_by_fileuid(
        self, db: Session, fileuid: UUID
    ) -> List[FileSecurityMappingDTO]:
        """
        Get file security mappings by fileuid.
        Replicates GetFileSecurityByFileuid from .NET.

        Note: The .NET code uses a stored procedure [alts].[GetFileSecurityByFileuid],
        but since stored procedures are not in use, we implement this as a direct query.
        """
        try:
            from src.domain.entities.file_security_mapping import FileSecurityMapping

            logger.info(f"GetFileSecurityByFileUID: fileuid={fileuid}")

            # Query file security mappings
            # This replicates the stored procedure logic
            security_mappings = (
                db.query(FileSecurityMapping)
                .filter(
                    FileSecurityMapping.fileuid == fileuid,
                    FileSecurityMapping.isactive == True,
                )
                .all()
            )

            # Convert to DTOs
            result = [
                FileSecurityMappingDTO.model_validate(mapping)
                for mapping in security_mappings
            ]

            logger.info(
                f"GetFileSecurityByFileUID: Found {len(result)} security mappings"
            )
            return result

        except Exception as ex:
            logger.error(f"GetFileSecurityByFileUID error: {ex}", exc_info=True)
            return []

    def get_extract_files_by_file_uid(self, db: Session, fileuid: UUID) -> List[Any]:
        """
        Replicates GetExtractFilesByFileUIDAsync logic.
        """
        try:
            from src.domain.entities.extract_file import ExtractFile

            logger.info(f"GetExtractFilesByFileUIDAsync: fileuid={fileuid}")

            results = (
                db.query(ExtractFile)
                .filter(ExtractFile.fileuid == fileuid, ExtractFile.isactive == True)
                .all()
            )

            return results
        except Exception as ex:
            logger.error(f"GetExtractFilesByFileUIDAsync error: {ex}", exc_info=True)
            raise

    def add_file_comment(
        self, db: Session, fileuid: UUID, comment: str, createdby: str
    ) -> bool:
        """
        Updates FileManager record with a comment.
        """
        try:
            from src.domain.entities.file_manager import FileManager
            from datetime import datetime

            logger.info(f"AddFileComment: fileuid={fileuid}")

            # Fetch file
            file = db.query(FileManager).filter(FileManager.fileuid == fileuid).first()

            if not file:
                logger.error(f"AddFileComment: File not found for fileuid={fileuid}")
                return False

            # Update fields
            file.comments = comment
            file.statuscomment = "Comment Added"
            # file.updated = datetime.utcnow()
            # file.updatedby = created_by or "System"

            db.commit()
            logger.info(f"AddFileComment: Successfully updated fileuid={fileuid}")
            return True

        except Exception as ex:
            logger.error(f"AddFileComment error: {ex}", exc_info=True)
            db.rollback()
            return False

    def update_extract_file_api(
        self, db: Session, *, extract_file_detail, file_manager, file_activity
    ) -> None:
        """
        Persists UpdateExtractFileApi changes.
        NO business logic here.
        """
        try:
            if file_manager:
                db.add(file_manager)

            if extract_file_detail:
                db.add(extract_file_detail)

            if file_activity:
                db.add(file_activity)

            db.commit()

        except Exception as ex:
            logger.error("UpdateExtractFileApi DB error", exc_info=True)
            db.rollback()
            raise

    def get_active_extraction_file_detail(
        self, db: Session, fileuid: UUID
    ) -> ExtractionFileDetail | None:
        return (
            db.query(ExtractionFileDetail)
            .filter(
                ExtractionFileDetail.fileuid == fileuid,
                ExtractionFileDetail.isactive == True,
            )
            .first()
        )

    def get_file_manager_by_fileuid(
        self, db: Session, fileuid: UUID
    ) -> FileManager | None:
        return db.query(FileManager).filter(FileManager.fileuid == fileuid).first()

    def file_exists(self, db, fileuid: UUID):
        return db.query(FileManager).filter(FileManager.fileuid == fileuid).first()

    def save_file_received(self, db, file: dict, is_manually: bool):

        # folder_name = datetime.utcnow().strftime("%d%b%Y")

        # # Structured vs unstructured logic
        # if file.get("category") == "Structured":
        #     file_name = file["filename"]
        # else:
        #     file_name = str(file["fileuid"])

        # # 🔹 Azure upload (THIS WAS MISSING)
        # blob_path = self.uploader.upload_base64(
        #     base64_content=file["content"],
        #     file_name=file_name,
        #     folder=folder_name,
        # )

        # Update file path after upload
        # file["file_path"] = blob_path
        file.pop("content", None)  # store this file on the azure devops
        entity = FileManager(**file)
        db.add(entity)
        db.commit()
        return 1

    # def save_document_activity(self, db, fileuid, status_comment: str):
    #     activity = DocumentActivity(
    #         fileuid=fileuid,
    #         status="Captured",
    #         stage="DocReady",
    #         document_processing_stage="DocumentCapture",
    #         status_comment=status_comment,
    #     )
    #     db.add(activity)
    #     db.commit()

    def get_file_by_fileuid(self, db: Session, fileuid: UUID) -> Optional[FileManager]:
        return (
            db.query(FileManager)
            .filter(FileManager.fileuid == fileuid, FileManager.isactive == True)
            .first()
        )

    def update_file(self, db: Session, file: FileManager):
        db.merge(file)
        db.flush()

    def get_file_activities(self, db: Session, fileuid: UUID):
        return (
            db.query(FileActivity)
            .filter(FileActivity.fileuid == fileuid, FileActivity.isactive == True)
            .order_by(FileActivity.created.desc())
            .all()
        )

    def add_process_log(self, db: Session, process_log: FileProcessLog):
        db.add(process_log)
        db.flush()

    def add_activity(self, db: Session, activity: FileActivity):
        db.add(activity)
        db.flush()

    # Alias to match service layer expectation
    def get_file(self, db: Session, fileuid: UUID):
        return self.get_file_by_fileuid(db, fileuid)

