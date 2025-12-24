from typing import Dict
from datetime import datetime
from uuid import UUID
from src.domain.entities.file_manager import FileManager
from src.domain.entities.file_process_log import FileProcessLog
from src.domain.entities.file_activity import FileActivity

class ApproveDocumentResultEnricher:
    """
    Enrich the results of the approve document logic
    - Prepares response dictionary
    - Builds process log and activity entities
    """

    def enrich(
        self,
        file: FileManager,
        duplicate_sid: UUID | None,
        updated_by: str = "SYSTEM",
        comment: str | None = None
    ) -> Dict:
        """
        Return response dictionary
        """
        if duplicate_sid:
            return {
                "result_code": "400",
                "total": 0,
                "data": None,
                "result_message": (
                    f"SID: {duplicate_sid} is linked to multiple accounts. "
                    "Either ignore the SID or change the linked SID for the duplicated account."
                ),
            }

        return {
            "result_code": "Success",
            "total": 1,
            "data": None,
            "result_message": "Document approved successfully",
        }

    def build_process_log(
        self, file: FileManager, updated_by: str = "SYSTEM"
    ) -> FileProcessLog:
        """
        Build a FileProcessLog entity
        """
        return FileProcessLog(
            fileuid=file.fileuid,
            status="Approved",
            stage="Approved",
            statuscomment="Manual document approved.",
            filetype=file.filetypegenai,
            createdby=len(updated_by),
            created=datetime.utcnow(),
            isactive=file.isactive
        )

    def build_activity(
        self, file: FileManager, updated_by: str = "SYSTEM", comment: str | None = None
    ) -> FileActivity:
        """
        Build a FileActivity entity
        """
        return FileActivity(
            fileuid=file.fileuid,
            status=file.status,
            stage="Approved",
            comment="Document approved successfully",
            statuscomment=comment,
            created = datetime.utcnow(),
            createdby=len(updated_by),
            isactive=file.isactive
        )