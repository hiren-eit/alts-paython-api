"""
PostgreSQL File Manager Repository
Clean implementation using separated query builder and result enricher.
"""
from typing import List, Any, Dict

from sqlalchemy.orm import Session

from sqlalchemy import func, cast, String, case, and_, or_, distinct
from sqlalchemy.orm import Session
from uuid import UUID

from src.domain.entities.file_manager import FileManager
from src.domain.entities.extract_file import ExtractFile
from src.domain.entities.file_configuration import FileConfiguration
from src.domain.entities.account_master import AccountMaster
from src.domain.interfaces.file_activity_repository_interface import IFileActivityRepository
from src.domain.dtos.file_manager_dto import ApproveFileRequest, FileManagerFilter
from src.infrastructure.database.query_builders import (
    FileManagerQueryBuilder,
    FileManagerResultEnricher,
)
from src.infrastructure.database.query_builders.file_activity_log_query_builder import (
    FileActivityLogQueryBuilder
)
from src.domain.dtos.file_activity_dto import FileActivityResponse
from src.infrastructure.database.query_builders.file_details_query_builder import FileDetailsQueryBuilder
from src.infrastructure.database.query_builders.file_details_result_enricher import FileDetailsResultEnricher
from src.infrastructure.logging.logger_manager import get_logger
from src.domain.dtos.file_details_dto import FileDetailsResponse
from uuid import UUID

logger = get_logger(__name__)

class FileActivityRepository(IFileActivityRepository):
    """PostgreSQL implementation of FileManager repository using SQLAlchemy ORM"""

    def get_file_manager_list(
        self, 
        db: Session, 
        filters: FileManagerFilter
    ) -> Dict:
        """
        Replicates GetFileManager stored procedure logic.
        Uses separated QueryBuilder and ResultEnricher for clean code.
        """
        try:
            logger.info(f"GetFileManagerList: status={filters.file_status}, fileType={filters.file_type}")
            
            # Build query with all filters
            query_builder = FileManagerQueryBuilder(db, filters)
            query_builder.build_query()
            
            # Get count and results
            total_count = query_builder.get_count()
            results = query_builder.get_results()
            
            # Enrich results with account info and SLA calculations
            enricher = FileManagerResultEnricher(db, filters)
            items = enricher.enrich(results)
            
            logger.info(f"GetFileManagerList: returned {len(items)} items, total={total_count}")
            
            return {
                "total": total_count,
                "page": filters.page_number,
                "page_size": filters.page_size,
                "data": items
            }
            
        except Exception as ex:
            logger.error(f"GetFileManagerList error: {ex}", exc_info=True)
            raise

    # def get_file_details_by_fileuid(
    #     self,
    #     db: Session,
    #     fileuid: UUID
    # ) -> FileDetailsResponse:
    #     """
    #     Replicates GetFileDetailsByFileUID stored procedure logic.
    #     Uses separated QueryBuilder and ResultEnricher for clean code.
    #     """
    #     try:
    #         logger.info(f"GetFileDetailsByFileUID: fileuid={fileuid}")

    #         # 1. Build query
    #         query_builder = FileDetailsQueryBuilder(db, str(fileuid))
    #         query_builder.build_query()
            
    #         # 2. Fetch raw DB record (single row)
    #         result = query_builder.get_one()
            
    #         if not result:
    #             logger.info(f"GetFileDetailsByFileUID: No file found for {fileuid}")
    #             return {
    #                 "total": 0,
    #                 "data": []
    #             }

    #         # 3. Enrich result
    #         enricher = FileDetailsResultEnricher(db)
    #         enriched = enricher.enrich(result)

    #         logger.info(f"GetFileDetailsByFileUID: returning details for {fileuid}")
            
    #         # Wrap in paginated structure to match likely API requirements
    #         return {
    #             "total": 1,
    #             "data": [enriched]
    #         }

    #     except Exception as ex:
    #         logger.error(f"GetFileDetailsByFileUID error: {ex}", exc_info=True)
    #         raise

    # def get_file_details_by_fileuid(self, db: Session, fileuid: UUID):
    #     D = FileManager
    #     ED = ExtractFile
    #     AM = AccountMaster
    #     DC = FileConfiguration

    #     # ----------------------------
    #     # Aggregations (correlated subqueries)
    #     # ----------------------------
    #     batch_sq = (
    #         db.query(
    #             func.string_agg(distinct(cast(ED.batchid, String)), ', ')
    #         )
    #         .filter(
    #             ED.fileuid == D.fileuid,
    #             ED.isignored.is_(False)
    #         )
    #         .correlate(D)
    #         .scalar_subquery()
    #     )

    #     firm_sq = (
    #         db.query(
    #             func.string_agg(distinct(cast(AM.firm_id, String)), ', ')
    #         )
    #         .select_from(ED)
    #         .join(
    #             AM,
    #             and_(
    #                 ED.account_uid == AM.account_uid,
    #                 ED.account_sid == AM.accounts_id
    #             )
    #         )
    #         .filter(
    #             ED.fileuid == D.fileuid,
    #             ED.isignored.is_(False)
    #         )
    #         .correlate(D)
    #         .scalar_subquery()
    #     )

    #     business_date_sq = (
    #         db.query(
    #             func.string_agg(distinct(cast(ED.businessdate, String)), ', ')
    #         )
    #         .filter(
    #             ED.fileuid == D.fileuid,
    #             ED.isignored.is_(False)
    #         )
    #         .correlate(D)
    #         .scalar_subquery()
    #     )

    #     # ----------------------------
    #     # SLA Status CASE
    #     # ----------------------------
    #     sla_status = case(
    #         (D.age < DC.sla_days, "Within SLA"),
    #         (D.age == DC.sla_days, "On SLA"),
    #         (D.age > DC.sla_days, "SLA Breached"),
    #         else_=None
    #     )

    #     # ----------------------------
    #     # Main Query
    #     # ----------------------------
    #     row = (
    #         db.query(
    #             D.fileid,
    #             D.fileuid,
    #             D.filename,
    #             D.age,
    #             D.ingestionfailedimageurl,
    #             D.file_metadata.label("metadata"),
    #             D.category,
    #             DC.sla_days,
    #             D.created,
    #             func.concat(cast(D.age, String), "/", cast(DC.sla_days, String)).label("age_sla_display"),
    #             D.status,
    #             D.stage,
    #             D.failurestage,
    #             D.statusdate,
    #             D.harvestsource,
    #             D.method,
    #             batch_sq.label("batch"),
    #             D.filetypeproceesrule,
    #             # firm_sq.label("firm_id"),
    #             # D.capturemethod,
    #             # D.linkingmethod,
    #             D.extractsystem,
    #             D.filetypegenai,
    #             sla_status.label("sla_status"),
    #             business_date_sq.label("business_date")
    #         )
    #         .outerjoin(
    #             DC,
    #             and_(
    #                 DC.isactive.is_(True),
    #                 or_(
    #                     and_(
    #                         D.status.in_(["Captured", "Extract", "Update", "Failed"]),
    #                         DC.configuration_name == D.filetypeproceesrule
    #                     ),
    #                     and_(
    #                         or_(
    #                             D.status.in_(["Linked", "Approved"]),
    #                             and_(
    #                                 D.status == "Failed",
    #                                 D.failurestage == "Failed Ingestion"
    #                             )
    #                         ),
    #                         DC.configuration_name == D.filetypegenai
    #                     )
    #                 )
    #             )
    #         )
    #         .filter(
    #             D.isactive.is_(True),
    #             D.fileuid == fileuid
    #         )
    #         .one_or_none()
    #     )

    #     if not row:
    #         return {"total": 0, "data": []}

    #     return {"total": 1, "data": [dict(row._mapping)]}


    def get_file_details_by_fileuid(
        self,
        db: Session,
        fileuid: UUID
    ) -> Dict:
        """
        Get file details by FileUID.
        Uses QueryBuilder and ResultEnricher for clean architecture.
        """
        try:
            logger.info(f"GetFileDetailsByFileUID: fileuid={fileuid}")

            query_builder = FileDetailsQueryBuilder(db, fileuid)
            result = query_builder.get_file()

            if not result:
                return {"total": 0, "data": []}

            enricher = FileDetailsResultEnricher(db)
            item = enricher.enrich(result)

            return {
                "total": 1,
                "data": [item]
            }

        except Exception as ex:
            logger.error(f"GetFileDetailsByFileUID error: {ex}", exc_info=True)
            raise

    
    
    def get_file_activity(self, db: Session, fileuid: UUID) -> List[FileActivityResponse]:
        """Retrieve file activity logs for a given file UID."""
        logger.info(f"GetFileActivity: fileuid={fileuid}")
        # TODO: Implement actual query logic. Returning empty list as placeholder.
        query_builder = FileActivityLogQueryBuilder(db, fileuid)
        query_builder.build_query()
        return query_builder.get_results()

    def approve_file(
        self,
        db: Session,
        file: ApproveFileRequest,
        
    ) -> Dict:
        """
        This replicates the ApproveFile endpoint,
        """
        try:
            logger.info(f"ApproveFile: fileuid={file.file_uid}")

            logger.info(f"ApproveFile: file approval for {file.file_uid}")
            return {
                "result_code": "Success",
                "total": 0,
                "data": None,
                "result_message": "File approved successfully"
            }

        except Exception as ex:
            logger.error(f"ApproveFile error: {ex}", exc_info=True)
            raise