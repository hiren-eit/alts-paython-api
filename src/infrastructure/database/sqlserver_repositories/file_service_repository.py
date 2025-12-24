from typing import Dict

from sqlalchemy.orm import Session

from src.domain.dtos.document_receiver_dto import DocumentRequestModel
from src.domain.interfaces.file_service_repository_interface import IFileServiceRepository
from src.infrastructure.logging.logger_manager import get_logger

logger = get_logger(__name__)

class FileServiceRepository(IFileServiceRepository):
    def document_retrieval(
        self,
        db: Session,
        documents: DocumentRequestModel
    ) -> Dict:
        """
        Upload file.
        This endpoint replicates the /DocumentRetrieval API from .NET
        """
        try:
            logger.info("DocumentRetrieval")
            return {
                "result_code": "SUCCESS",
                "total": 1,
                "data": [
                    {
                        "docUID": "9e31c8a0-c6ad-48a6-aff7-77446c305687",
                        "fileName": "Free_Test_Data_100KB_PDF.pdf",
                        "status": "Success",
                        "message": "Your document has been uploaded successfully. Document ID: 9e31c8a0-c6ad-48a6-aff7-77446c305687"
                    }
                ],
                "result_message": "Documents processed"
            }
        except Exception as ex:
            logger.error(f"DocumentRetrieval error: {ex}", exc_info=True)
            raise