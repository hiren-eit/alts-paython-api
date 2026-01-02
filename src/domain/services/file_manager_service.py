from src.domain.dtos.file_manager_dto import ApproveFileRequest
from typing import List, Set
from collections import defaultdict
from datetime import datetime
import uuid
import base64
from uuid import UUID

from fastapi import status
from sqlalchemy.orm import Session

from src.infrastructure.logging.logger_manager import get_logger
from src.domain.dtos.response_object import ResponseObject
from src.domain.dtos.file_request_dto import FileRequestDTO
from src.domain.dtos.file_manager_dto import FileManagerFilter, IgnoreFilesRequest
from src.domain.dtos.update_extract_file_dto import ResponseObjectModel
from src.domain.enums.file_porcess_log_enums import (
    FileFailureStage,
    FileProcessStatus,
    FileProcessStage,
)
from src.domain.entities.file_process_log import FileProcessLog
from src.domain.entities.file_activity import FileActivity
from src.domain.entities.file_manager import FileManager
from src.domain.interfaces.file_manager_repository_interface import (
    IFileManagerRepository,
)
from src.domain.dtos.file_manager_dto import FileManagerFilter, IgnoreFilesRequest
from src.utils.datetime_utils import parse_datetime
from src.utils.extraction_json_utils import (
    are_investor_account_names_unique,
    extract_portfolio_fields,
)

logger = get_logger(__name__)


class FileManagerService:
    def __init__(self, repository: IFileManagerRepository):
        self.repo = repository
        self.MAX_ALLOWED_SIZE = 1_073_741_824  # 1 GB
        self.MAX_FILE_COUNT = 50

    def get_file_manager_list(self, db: Session, filters: FileManagerFilter):
        """
        Get paginated file manager list with filters.
        Replicates GetFileManager stored procedure logic.
        """
        return self.repo.get_file_manager_list(db, filters)

    def get_file_details_by_file_uid(self, db: Session, fileuid: UUID):
        """
        Get file details by fileuid.
        Replicates GetFileDetailsByFileUID stored procedure logic.
        """
        return self.repo.get_file_details_by_file_uid(db, fileuid)

    def get_manual_extraction_config_fields_by_id(
        self, db: Session, fileConfigurationId: int
    ):
        """
        Get manual extraction config fields by id.
        Replicates GetManualExtractionConfigFieldsById stored procedure logic.
        """
        return self.repo.get_manual_extraction_config_fields_by_id(
            db, fileConfigurationId
        )

    def get_extract_file_api(self, db: Session, fileuid: UUID):
        """
        Get extract file api.
        """
        return self.repo.get_extract_file_api(db, fileuid)

    def get_extract_files_by_file_uid(self, db: Session, fileuid: UUID):
        """
        Get extract files by file_uid.
        Replicates GetExtractFilesByFileUIDAsync logic.
        """
        return self.repo.get_extract_files_by_file_uid(db, fileuid)

    def add_file_comment(
        self, db: Session, fileuid: UUID, comment: str, createdby: str
    ) -> bool:
        """
        Add a comment to a file.
        """
        if fileuid is None:
            logger.error("add_file_comment: fileuid not found.")
            return False

        file_detail = self.repo.get_file(db, fileuid)
        if not file_detail:
            logger.error(f"add_file_comment: No data found for fileuid: {fileuid}")
            return False

        try:
            # Update FileManager
            file_detail.comments = comment
            file_detail.statuscomment = "Comment Added"
            file_detail.updated = datetime.utcnow()
            file_detail.updatedby = createdby or "SYSTEM"
            file_detail.stage = FileProcessStage.Manual.value

            self.repo.update_file(db, file_detail)

            activity = FileActivity(
                fileuid=fileuid,
                status=file_detail.status,
                stage=file_detail.stage,
                statuscomment=file_detail.comments,  # User comment
                comment=file_detail.statuscomment,  # "Comment Added"
                createdby=createdby or "SYSTEM",
                iscommented=True,
                created=datetime.utcnow(),
                isactive=True,
            )
            self.repo.add_activity(db, activity)

            file_type = file_detail.filetypegenai or file_detail.filetypeprocessrule

            # Map status and stage to enums for FileProcessLog
            status_enum = None
            if file_detail.status:
                try:
                    status_enum = FileProcessStatus(file_detail.status)
                except ValueError:
                    pass

            stage_enum = None
            if file_detail.stage:
                try:
                    stage_enum = FileProcessStage(file_detail.stage)
                except ValueError:
                    pass

            process_log = FileProcessLog(
                fileuid=file_detail.fileuid,
                status=status_enum,
                stage=stage_enum,
                filetype=file_type,
                fileprocessstage=file_detail.fileprocessstage,
                ruleid=None,
                remark=activity.comment,  # "Comment Added"
                statuscomment=activity.statuscomment,  # User comment
                createdby=createdby or "SYSTEM",
                created=datetime.utcnow(),
                isactive=True,
            )
            self.repo.add_process_log(db, process_log)

            db.commit()
            logger.info(
                "FileManagerService: Successfully inserted data into FileActivity and FileProcessLog."
            )
            return True

        except Exception as ex:
            logger.error(
                f"FileManagerService: Error while inserting data into FileActivity and FileProcessLog: {ex}",
                exc_info=True,
            )
            db.rollback()
            return False

    def update_extract_file(
        self, db, *, extract_file_detail, file_manager, request
    ) -> ResponseObjectModel:
        """
        BUSINESS LOGIC ONLY
        """

        old_json = extract_file_detail.extraction_data
        new_json = request.extraction_file_detail.extracteddata

        # 1. Investor + Account uniqueness
        if not are_investor_account_names_unique(new_json):
            return ResponseObjectModel(
                resultcode="ERROR",
                resultmessage="Investor or Account name already exists",
            )

        old_fields = extract_portfolio_fields(old_json)
        new_fields = extract_portfolio_fields(new_json)

        # 2. Configuration change
        is_configuration_changed = (
            request.extraction_file_detail.classification
            and extract_file_detail.classification
            != request.extraction_file_detail.classification
        )

        # 3. Business date logic
        old_date = (
            parse_datetime(old_fields.transaction_date)
            if extract_file_detail.classification in ("Distribution", "CapCall")
            else parse_datetime(old_fields.period_ending_dt)
        )

        new_date = (
            parse_datetime(new_fields.transaction_date)
            if request.extraction_file_detail.classification
            in ("Distribution", "CapCall")
            else parse_datetime(new_fields.period_ending_dt)
        )

        is_modified = (
            old_fields.investor != new_fields.investor
            or old_fields.account != new_fields.account
            or old_date != new_date
        )

        target_status = None
        target_stage = None
        try:
            target_status = FileProcessStatus(file_manager.status)
            target_stage = FileProcessStage(file_manager.stage)
        except (ValueError, AttributeError):
            target_status = FileProcessStatus.Update
            target_stage = FileProcessStage.Manual

        # 4. Apply business intent
        if is_configuration_changed or is_modified:
            target_status = FileProcessStatus.Extract
            target_stage = FileProcessStage.ExtractReceived

            file_manager.status = target_status.value
            file_manager.stage = target_stage.value
            file_manager.updated = datetime.utcnow()
            file_manager.updatedby = request.updatedby
            file_manager.fileprocessstage = "ManualLinkToExtract"
            file_manager.filetypegenai = request.extraction_file_detail.classification
            file_manager.filetypeprocessrule = (
                request.extraction_file_detail.classification
            )
            file_manager.statusdate = datetime.utcnow()
            file_manager.extractsystem = "Aithon Frame"
            file_manager.extractmethod = "Manual"
            file_manager.reason = "File extracted and classified successfully"

        # 5. Update extraction detail
        extract_file_detail.extraction_data = new_json
        extract_file_detail.isupdate = True
        extract_file_detail.type = "File Manager UX"
        extract_file_detail.updatedby = request.updatedby

        if is_configuration_changed:
            extract_file_detail.classification = (
                request.extraction_file_detail.classification
            )

        # Log the activity
        self._log(
            db,
            file=file_manager,
            status=target_status,
            stage=target_stage,
            message="Manually updated extracted data",
            comments=None,
            updated_by=request.updatedby,
        )

        # 6. Persist (delegated)
        self.repo.update_extract_file_api(
            db,
            extract_file_detail=extract_file_detail,
            file_manager=file_manager,
            file_activity=None,  # Already handled by _log
        )

        return ResponseObjectModel(
            resultcode="SUCCESS", resultmessage="Update File save successful"
        )

    def file_retrieval(self, db: Session, request: FileRequestDTO):
        """
        need to add the file activity and file upload to azure code - pending
        """
        response = ResponseObject()

        if not request.files:
            response.result_code = str(status.HTTP_500_INTERNAL_SERVER_ERROR)
            response.result_message = "File Detail null"
            response.count = 0
            response.result_object = None
            return response

        if len(request.files) > self.MAX_FILE_COUNT:
            response.result_code = str(status.HTTP_500_INTERNAL_SERVER_ERROR)
            response.result_message = "Maximum 50 files allowed"
            return response

        total_size = 0
        processed_names: Set[str] = set()
        results = []

        # ---------- size + duplicate validation ----------
        for item in request.files:
            try:
                decoded = base64.b64decode(item.file)
            except Exception:
                logger.error("Invalid base64 for file %s", item.filename)
                continue

            total_size += len(decoded)

            if item.filename in processed_names:
                logger.error("Duplicate detected: %s", item.filename)
                continue

            processed_names.add(item.filename)

        if total_size > self.MAX_ALLOWED_SIZE:
            response.result_code = str(status.HTTP_500_INTERNAL_SERVER_ERROR)
            response.result_message = "Total upload size exceeds 1 GB"
            return response

        # ---------- processing ----------
        for item in request.files:
            file_uid = uuid.uuid4()

            if not file_uid:
                logger.error("Invalid doc_id for file %s", item.filename)
                continue

            existing_file = self.repo.file_exists(db, file_uid)
            if existing_file:
                self._log(
                    db,
                    file=existing_file,
                    status=FileProcessStatus.Duplicate,
                    stage=FileProcessStage.New,
                    message=f"File already exists with File ID: {file_uid}",
                    comments=None,
                    updated_by=request.created_by or "SYSTEM",
                )
                db.commit()
                continue

            extension = item.filename.split(".")[-1] if "." in item.filename else None
            folder_name = datetime.utcnow().strftime("%d%b%Y")

            file_entity = {
                "fileuid": file_uid,
                "type": request.type,
                "filename": item.filename,
                "content": item.file,
                "fileextension": extension,
                "filepath": f"{folder_name}/{file_uid}",
                "method": "Haas" if request.haas else "AUTOMATED",
                "harvestsource": request.harvest_source,
                "capturemethod": "Manual",
                # "capture_system": "Manual", # not in the FileManager right now
                "createdby": request.created_by or "SYSTEM",
                "created": datetime.utcnow(),
                "statusdate": datetime.utcnow(),
                "isactive": True,
            }

            rows = self.repo.save_file_received(
                db=db,
                file=file_entity,
                is_manually=True,
            )

            if rows:
                results.append({"file_uid": str(file_uid)})
                # Log success
                self._log(
                    db,
                    file=FileManager(fileuid=file_uid),
                    status=FileProcessStatus.NewFile,
                    stage=FileProcessStage.New,
                    message=f"File received: {item.filename}",
                    comments=None,
                    updated_by=request.created_by or "SYSTEM",
                )
                db.commit()

        response.result_code = str(status.HTTP_200_OK)
        response.result_message = "files processed"
        response.count = len(results)
        response.result_object = results

        return response

    async def replay_files(
        self, db: Session, fileuids: List[UUID], comment: str, updatedby: str
    ) -> int:
        """
        need to add the logs and password rule process
        """
        processed_count = 0
        for uid in fileuids:
            file = self.repo.get_file_by_fileuid(db, uid)
            if not file:
                continue

            old_status = file.status

            # Apply your existing password rule
            if (
                file.reason
                and "invalid_password" in file.reason.lower()
                or not file.password
            ):
                # await self.apply_password_rule(file.fileuids)
                pass

            target_status = None
            target_stage = None

            # Map FailureStage to new Status/Stage
            if file.failurestage == "FailedLinking" and file.status == "Failed":
                target_status = FileProcessStatus.Extract
                target_stage = FileProcessStage.ExtractReceived
                file.reason = "File replayed Failed Linked to Extract"
            elif file.failurestage == "FailedExtraction" and file.status == "Failed":
                target_status = FileProcessStatus.Captured
                target_stage = FileProcessStage.DocReady
                file.reason = "File replayed Failed Extracted to Captured"
                file.replay = True
            elif file.failurestage == "FailedIngestion" and file.status == "Failed":
                target_status = FileProcessStatus.Approved
                target_stage = FileProcessStage.Approved
                file.reason = "File replayed Failed Ingestion to Approved"
            elif file.failurestage == "FailedCapture" and file.status == "Failed":
                target_status = FileProcessStatus.Captured
                target_stage = FileProcessStage.DocReady
                file.reason = "File replayed Failed Capture to Captured"
            else:
                continue

            file.status = target_status.value
            file.stage = target_stage.value
            file.status_comment = (
                f"Replay: moved '{old_status}' to '{target_status.value}'"
            )
            file.comments = comment
            file.failure_stage = None
            file.updated = datetime.utcnow()
            file.updated_by = updatedby or "SYSTEM"

            self.repo.update_file(db, file)

            # Save logs
            self._log(
                db,
                file=file,
                status=target_status,
                stage=target_stage,
                message=file.status_comment,
                comments=comment,
                updated_by=updatedby,
            )

            processed_count += 1

        return processed_count

    async def update_file_status(self, db: Session, request: IgnoreFilesRequest) -> int:
        result = 0
        updated_by = request.updated_by or "SYSTEM"

        fileuids = self._parse_fileuids(request.fileuids)

        for fileuid in fileuids:
            file = self.repo.get_file(db, fileuid)
            if not file:
                continue

            if request.status == FileProcessStatus.Ignored.value:
                self._move_to_ignored(db, file, updated_by, request.comments)
                result += 1
                continue

            if request.status == FileProcessStatus.InProgress.value:
                if self._restore_from_ignored(db, file, updated_by, request.comments):
                    result += 1

        db.commit()
        return result

    async def approve_file(
        self, db: Session, request: ApproveFileRequest
    ) -> ResponseObjectModel:
        """
        Approve a file for ingestion.
        """
        try:
            # 1. Get file detail
            file_detail = self.repo.get_file(db, request.fileUid)
            if not file_detail:
                logger.warning(
                    f"ApproveFile: File with fileUid {request.fileUid} not found."
                )
                return ResponseObjectModel(
                    resultcode="ERROR", resultmessage="File detail not found."
                )

            # 2. Check if has linked account
            extract_files = self.repo.get_extract_files_by_file_uid(db, request.fileUid)
            linked_files = [x for x in extract_files if x.islinked and not x.isignored]

            if not linked_files:
                logger.warning(
                    f"ApproveFile: No active linked extract file found for fileUid {request.fileUid}."
                )
                return ResponseObjectModel(
                    resultcode="ERROR",
                    resultmessage="Please link at least one account before approving the file.",
                )

            # 3. Check for duplicates by account_sid
            from collections import Counter

            account_sids = [x.account_sid for x in linked_files if x.account_sid]
            sid_counts = Counter(account_sids)
            duplicate_sid = next(
                (sid for sid, count in sid_counts.items() if count > 1), None
            )

            if duplicate_sid:
                return ResponseObjectModel(
                    resultcode="400",
                    resultmessage=f"SID: {duplicate_sid} is linked to multiple accounts. Either ignore the SID or change the linked SID for the duplicated account.",
                )

            # 4. Update file status
            file_detail.status = FileProcessStatus.Approved.value
            file_detail.statusdate = datetime.utcnow()
            file_detail.stage = FileProcessStage.Approved.value
            file_detail.reason = "File is ready for ingestion."
            file_detail.updatedby = request.updatedby or "SYSTEM"
            file_detail.updated = datetime.utcnow()
            file_detail.statuscomment = "File approved successfully."

            self.repo.update_file(db, file_detail)

            # 5. Save logs
            self._log(
                db,
                file=file_detail,
                status=FileProcessStatus.Approved,
                stage=FileProcessStage.Approved,
                message="File approved successfully.",
                comments=request.comment,
                updated_by=request.updatedby or "SYSTEM",
                process_message="Manual file approved.",
            )

            db.commit()
            logger.info(f"ApproveFile: File approved for fileUid {file_detail.fileuid}")

            return ResponseObjectModel(
                resultcode="SUCCESS", resultmessage="File approved successfully."
            )

        except Exception as ex:
            logger.error(
                f"ApproveFile: Error occurred while approving file with fileUid {request.fileUid}: {ex}",
                exc_info=True,
            )
            db.rollback()
            return ResponseObjectModel(
                resultcode="ERROR",
                resultmessage="An error occurred while approving the file. Please try again later.",
            )

    # ======================================================================
    # IGNORED
    # ======================================================================
    def _move_to_ignored(self, db, file, updated_by, comments):
        now = datetime.utcnow()

        file.status = FileProcessStatus.Ignored.value
        file.stage = FileProcessStage.Ignored
        file.statusdate = now
        file.statuscomment = "Manually moved to Ignored"
        file.reason = "File manually moved to Ignored"
        file.ignoredby = updated_by
        file.ignoredon = now
        file.updated = now
        file.updatedby = updated_by
        file.failurestage = None

        self.repo.update_file(db, file)

        self._log(
            db,
            file=file,
            status=FileProcessStatus.Ignored,
            stage=FileProcessStage.Ignored,
            message="Manually moved to Ignored",
            comments=comments,
            updated_by=updated_by,
        )

    # ======================================================================
    # RESTORE FROM IGNORED (STATE MACHINE)
    # ======================================================================
    def _restore_from_ignored(self, db, file, updated_by, comments) -> bool:
        prev = self._get_previous_state(db, file.fileuid)
        if not prev:
            return False

        # -------- Failure-specific transitions --------
        if prev.status == FileProcessStatus.Failed.value and prev.failurestage in [
            e.value for e in FileFailureStage
        ]:
            message = f"File process from Ignored to {prev.failurestage}"
            self._apply_restore(
                db,
                file=file,
                status=FileProcessStatus.Failed,
                stage=FileProcessStage(prev.stage),
                failure_stage=prev.failurestage,
                message=message,
                comments=comments,
                updated_by=updated_by,
            )
            return True

        # -------- Captured → DocReady --------
        if (
            prev.status == FileProcessStatus.Captured.value
            and prev.stage == FileProcessStage.DocReady.value
        ):
            self._apply_restore(
                db,
                file=file,
                status=FileProcessStatus.Captured,
                stage=FileProcessStage.DocReady,
                message="File process from Ignored to Captured",
                comments=comments,
                updated_by=updated_by,
            )
            return True

        # -------- Default (includes Ingestion In Progress → Approved) --------
        new_status = (
            FileProcessStatus.Approved
            if prev.status == "Ingestion In Progress"
            else FileProcessStatus(prev.status)
        )

        self._apply_restore(
            db,
            file=file,
            status=new_status,
            stage=FileProcessStage(prev.stage),
            message=f"File process from Ignored to {new_status.value}",
            comments=comments,
            updated_by=updated_by,
        )
        return True

    # ======================================================================
    # SHARED RESTORE LOGIC (no duplication, same behavior)
    # ======================================================================
    def _apply_restore(
        self,
        db,
        file,
        status,
        stage,
        message,
        comments,
        updated_by,
        failure_stage=None,
    ):
        now = datetime.utcnow()

        file.status = status.value
        file.stage = stage
        file.statusdate = now
        file.updated = now
        file.updatedby = updated_by
        file.failurestage = failure_stage
        file.reason = message
        file.statuscomment = message

        self.repo.update_file(db, file)

        self._log(
            db,
            file=file,
            status=status,
            stage=stage,
            message=message,
            comments=comments,
            updated_by=updated_by,
            failure_stage=failure_stage,
        )

    # ======================================================================
    # LOGGING (ProcessLog + Activity)
    # ======================================================================
    def _log(
        self,
        db,
        file,
        status,
        stage,
        message,  # System action message (Activity.comment)
        comments,  # User comment (Activity.statuscomment)
        updated_by,
        failure_stage=None,
        process_message=None,  # ProcessLog.statuscomment (if different from message)
    ):
        now = datetime.utcnow()

        # Extract extra fields from file object if available
        file_type = getattr(file, "filetypegenai", None) or getattr(
            file, "filetypeprocessrule", None
        )
        file_process_stage = getattr(file, "fileprocessstage", None)

        # FileProcessLog: statuscomment is the system message
        self.repo.add_process_log(
            db,
            FileProcessLog(
                fileuid=file.fileuid,
                status=status,
                stage=stage,
                filetype=file_type,
                fileprocessstage=file_process_stage,
                createdby=updated_by,
                statuscomment=process_message or message,
                created=now,
                updated=now,
                isactive=True,
            ),
        )

        # FileActivity: statuscomment is the user comment, comment is the system message
        self.repo.add_activity(
            db,
            FileActivity(
                fileuid=file.fileuid,
                status=status.value,
                stage=stage.value,
                failurestage=failure_stage,
                statuscomment=comments,  # User comment
                comment=message,  # System action message
                createdby=updated_by,
                iscommented=True,
                created=now,
                updated=now,
                isactive=True,
            ),
        )

    # ======================================================================
    # ACTIVITY HISTORY
    # ======================================================================
    def _get_previous_state(self, db, fileuid):
        activities = self.repo.get_file_activities(db, fileuid)
        if not activities:
            return None

        grouped = defaultdict(list)
        for a in activities:
            grouped[(a.fileuid, a.status, a.stage)].append(a)

        deduped = [max(group, key=lambda x: x.created) for group in grouped.values()]

        deduped.sort(key=lambda x: x.created, reverse=True)

        return deduped[1] if len(deduped) > 1 else None

    # ======================================================================
    # UTIL
    # ======================================================================
    def _parse_fileuids(self, raw: str):
        ids = []
        for part in raw.split(","):
            try:
                ids.append(UUID(part.strip()))
            except Exception:
                pass
        return ids
