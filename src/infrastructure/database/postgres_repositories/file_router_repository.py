from typing import List, Dict
from uuid import UUID
from sqlalchemy.orm import Session
from src.domain.interfaces.file_router_repository_interface import IFileRouterRepository
from src.domain.entities.extract_file import ExtractFile
from src.infrastructure.logging.logger_manager import get_logger
from src.domain.dtos.resolve_file_update_dto import ResolveFileUpdate
from src.domain.entities.file_manager import FileManager
from src.domain.entities.file_activity import FileActivity
from src.infrastructure.database.query_builders.resolve_update_query_builder import ResolveUpdateQueryBuilder
from datetime import datetime, timezone

logger = get_logger(__name__)


class FileRouterRepository(IFileRouterRepository):
    """
    PostgreSQL implementation of FileRouter repository using SQLAlchemy ORM.
    Handles database operations related to file routing and extraction data.
    """

    def get_multiple_entities_or_investor(
        self,
        db: Session,
        file_uid: UUID
    ) -> List[ExtractFile]:
        """
        Retrieve a list of ExtractFile entities associated with a specific file UID.
        Replicates the logic of the 'GetMultipleEntitiesORInvestor' stored procedure.

        Args:
            db (Session): The database session.
            file_uid (UUID): The unique identifier of the file.

        Returns:
            List[ExtractFile]: A list of matching ExtractFile entities.

        Raises:
            Exception: If an error occurs during the database query.
        """
        try:
            logger.info(f"Fetching ExtractFile records for file_uid: {file_uid}")

            results = db.query(ExtractFile).filter(
                ExtractFile.fileuid == file_uid
            ).all()

            logger.info(f"Successfully fetched {len(results)} ExtractFile records for file_uid: {file_uid}")
            return results
        except Exception as ex:
            logger.error(f"Error fetching ExtractFile records for file_uid {file_uid}: {ex}", exc_info=True)
            raise

    def resolve_file_update(
        self,
        db: Session,
        resolveUpdate: ResolveFileUpdate,
    ) -> Dict:
        """
        Resolves file updates

        Args:
            db (Session): The database session.
            resolveUpdate (ResolveFileUpdate): An object contains selected fileuid and ignored fileuid.

        Returns:
            An object indicating the result of the resolution.

        Raises:
            Exception: If an error occurs during the database query.
        """
        try:
            logger.info(f"Resolving file update for file_uid: {resolveUpdate.selected_file_uid}")

            query_builder = ResolveUpdateQueryBuilder(db)

            selected_file = query_builder.get_file_by_file_uid(resolveUpdate.selected_file_uid)
            ignored_file = query_builder.get_file_by_file_uid(resolveUpdate.ignored_file_uid)

            if not selected_file or not ignored_file:
                return {
                    "result_code": "Error",
                    "result_message": "One or both files are not found."
                }
            
            # with db.begin():
            if selected_file.status == "Update":
                if(ignored_file.status == "Ingested" or ignored_file.stage == "Completed"):
                    return {
                        "result_code": "Error",
                        "result_message": (
                            f"Earlier files {ignored_file.fileuid}, {ignored_file.filename} already ingested. "
                            "This action will not ingest the updated file. "
                            "You may make changes to the existing position/transaction directly."
                        )
                    }
                    
                self._process_updated_file(
                    db,
                    query_builder,
                    selected_file,
                    ignored_file,
                    resolveUpdate.updatedby,
                    save_changes=False
                )

            else:
                query_builder.move_file_to_ignore(
                    ignored_file,
                    f"Updated file for earlier file UID {selected_file.fileuid} discarded by user",
                    "Update file discarded"
                )

                query_builder.add_file_activities(
                    self._build_selected_activity(selected_file, ignored_file, resolveUpdate.updatedby),
                    self._build_ignored_activity(selected_file, ignored_file, resolveUpdate.updatedby)
                )

            db.commit()

            logger.info(f"Successfully resolved updates for file_uid: {resolveUpdate.selected_file_uid}")
            return {
                "result_code": "Success",
                "result_message": "File processed successfully"
            }
        except Exception as ex:
            logger.error(f"Error resolving file updates for file_uid {resolveUpdate.selected_file_uid}: {ex}", exc_info=True)
            db.rollback()
            raise


    def _process_updated_file(
            self,
            db: Session,
            query_builder: ResolveUpdateQueryBuilder,
            selected_file: FileManager,
            ignored_file: FileManager,
            updated_by: str,
            save_changes: bool = True
    ):
        selected_file.status = "Extract"
        selected_file.updatefileid = None
        query_builder.update_file(selected_file)

        query_builder.add_file_activities(
            self._build_selected_activity(selected_file, ignored_file, updated_by),
            self._build_ignored_activity(selected_file, ignored_file, updated_by)
        )

        query_builder.move_file_to_ignore(
            ignored_file,
            f"Original file replaced by Update file UID {selected_file.fileuid} for Ingestion",
            "Replaced by Update file."
        )

        if save_changes:
            db.flush()


    def _build_selected_activity(self, selected_file: FileManager, ignored_file: FileManager, updated_by: str):
        return FileActivity(
            status="Extract",
            stage=selected_file.stage,
            statuscomment=(
                f"The Original file UID <a>{ignored_file.fileuid}</a> "
                "is discarded and moved to the Ignored grid"
            ),
            comment="Update Resolved",
            iscommented=True,
            fileuid=selected_file.fileuid,
            createdby=updated_by,
            created = datetime.now(timezone.utc),
            isactive = True
        )
    

    def _build_ignored_activity(self, selected_file: FileManager, ignored_file: FileManager, updated_by: str):
        return FileActivity(
            status="Ignored",
            stage="Ignored",
            statuscomment=(
                f"The file is replaced by file uid. <a>{selected_file.fileuid}</a>"
            ),
            comment="Ignored",
            iscommented=True,
            fileuid=ignored_file.fileuid,
            createdby=updated_by,
            created = datetime.now(timezone.utc),
            isactive = True
        )