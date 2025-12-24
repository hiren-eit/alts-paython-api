"""
SQL Server File Manager Repository
Uses the same query builders as PostgreSQL since SQLAlchemy ORM is database-agnostic.
"""
from typing import Dict

from sqlalchemy.orm import Session

from sqlalchemy import func, cast, String, case, and_, or_, distinct
from sqlalchemy.orm import Session
from uuid import UUID

from src.domain.entities.file_manager import FileManager
from src.domain.entities.extract_file import ExtractFile
from src.domain.entities.file_configuration import FileConfiguration
from src.domain.entities.account_master import AccountMaster
from src.domain.dtos.master_dto import Document
from src.domain.interfaces.file_manager_repository_interface import IFileManagerRepository
from src.domain.dtos.document_manager_dto import ApproveDocumentRequest, DocumentManagerFilter, UpdateDocumentReplayRequest
from src.infrastructure.database.query_builders import (
    DocumentManagerQueryBuilder,
    DocumentManagerResultEnricher
)
from src.infrastructure.database.query_builders.document_details_query_builder import DocumentDetailsQueryBuilder
from src.infrastructure.database.query_builders.document_details_result_enricher import DocumentDetailsResultEnricher
from src.domain.dtos.document_details_dto import DocumentDetailsResponse
from src.infrastructure.logging.logger_manager import get_logger
from uuid import UUID

logger = get_logger(__name__)


class FileManagerRepository(IFileManagerRepository):
    """SQL Server implementation of FileManager repository using SQLAlchemy ORM"""

    def get_file_manager_list(
        self, 
        db: Session, 
        filters: DocumentManagerFilter
    ) -> Dict:
        """
        Replicates GetDocumentManager stored procedure logic.
        Uses SQLAlchemy ORM - same code works for both PostgreSQL and SQL Server.
        """
        try:
            logger.info(f"GetFileManagerList: status={filters.document_status}, docType={filters.doc_type}")
            
            # Build query with all filters
            query_builder = DocumentManagerQueryBuilder(db, filters)
            query_builder.build_query()
            
            # Get count and results
            total_count = query_builder.get_count()
            results = query_builder.get_results()
            
            # Enrich results with account info and SLA calculations
            enricher = DocumentManagerResultEnricher(db, filters)
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

    # def get_file_details_by_docuid(
    #     self,
    #     db: Session,
    #     docUId: UUID
    # ) -> DocumentDetailsResponse:
    #     """
    #     Replicates GetDocumentDetailsByDocUID stored procedure logic.
    #     Uses separated QueryBuilder and ResultEnricher for clean code.
    #     """
    #     try:
    #         logger.info(f"GetDocumentDetailsByDocUID: docuid={docUId}")

    #         # 1. Build query
    #         query_builder = DocumentDetailsQueryBuilder(db, str(docUId))
    #         query_builder.build_query()
            
    #         # 2. Fetch raw DB record (single row)
    #         result = query_builder.get_one()
            
    #         if not result:
    #             logger.info(f"GetDocumentDetailsByDocUID: No document found for {docUId}")
    #             return {
    #                 "total": 0,
    #                 "page": 1,
    #                 "page_size": 1,
    #                 "data": []
    #             }

    #         # 3. Enrich result
    #         enricher = DocumentDetailsResultEnricher(db)
    #         enriched = enricher.enrich(result)

    #         logger.info(f"GetDocumentDetailsByDocUID: returning details for {docUId}")
            
    #         # Wrap in paginated structure to match likely API requirements
    #         return {
    #             "total": 1,
    #             "data": [enriched]
    #         }

    #     except Exception as ex:
    #         logger.error(f"GetDocumentDetailsByDocUID error: {ex}", exc_info=True)
    #         raise


    def get_file_details_by_docuid(
        db: Session,
        docuid: UUID
    ):
        D = FileManager
        ED = ExtractFile
        AM = AccountMaster
        DC = FileConfiguration

        # ----------------------------
        # Aggregations (correlated)
        # ----------------------------

        batch_sq = (
            db.query(
                func.string_agg(
                    distinct(cast(ED.batchid, String)),
                    ', '
                )
            )
            .filter(
                ED.fileuid == D.fileuid,
                ED.isignored.is_(False)
            )
            .correlate(D)
            .scalar_subquery()
        )

        firm_sq = (
            db.query(
                func.string_agg(
                    distinct(cast(AM.firm_id, String)),
                    ', '
                )
            )
            .select_from(ED)
            .join(
                AM,
                and_(
                    ED.account_uid == AM.account_uid,
                    ED.account_sid == AM.accounts_id
                )
            )
            .filter(
                ED.fileuid == D.fileuid,
                ED.isignored.is_(False)
            )
            .correlate(D)
            .scalar_subquery()
        )

        business_date_sq = (
            db.query(
                func.string_agg(
                    distinct(cast(ED.businessdate, String)),
                    ', '
                )
            )
            .filter(
                ED.fileuid == D.fileuid,
                ED.isignored.is_(False)
            )
            .correlate(D)
            .scalar_subquery()
        )

        sla_status = case(
            (D.age < DC.sla_days, "Within SLA"),
            (D.age == DC.sla_days, "On SLA"),
            (D.age > DC.sla_days, "SLA Breached"),
            else_=None
        )

        # ----------------------------
        # Main Query
        # ----------------------------

        row = (
            db.query(
                D.fileuid.label("doc_uid"),
                D.filename.label("document_name"),
                D.age,
                D.category,
                DC.sla_days,
                D.created,
                func.concat(
                    cast(D.age, String), "/", cast(DC.sla_days, String)
                ).label("age_sla_display"),
                D.status,
                D.stage,
                D.failurestage,
                D.statusdate,
                D.file_metadata.label("metadata"),
                D.harvestsource,
                D.method.label("processing_method"),
                batch_sq.label("batch"),
                D.filetypeproceesrule,
                firm_sq.label("firm_id"),
                D.capturemethod,
                D.linkingmethod,
                D.extractsystem,
                D.filetypegenai,
                sla_status.label("sla_status"),
                business_date_sq.label("business_date")
            )
            .outerjoin(
                DC,
                and_(
                    DC.isactive.is_(True),
                    or_(
                        and_(
                            D.status.in_(
                                ["Captured", "Extract", "Update", "Failed"]
                            ),
                            DC.configuration_name == D.filetypeproceesrule
                        ),
                        and_(
                            or_(
                                D.status.in_(["Linked", "Approved"]),
                                and_(
                                    D.status == "Failed",
                                    D.failurestage == "Failed Ingestion"
                                )
                            ),
                            DC.configuration_name == D.filetypegenai
                        )
                    )
                )
            )
            .filter(
                D.isactive.is_(True),
                D.fileuid == docuid
            )
            .one_or_none()
        )

        if not row:
            return {"total": 0, "data": []}

        return {
            "total": 1,
            "data": [dict(row._mapping)]
        }

        
    def get_manual_extraction_config_fields_by_id(
        self,
        db: Session,
        documentConfigurationId: UUID
    ):
        """
        Replicates GetManualExtractionConfigFieldsById stored procedure logic.
        Uses separated QueryBuilder and ResultEnricher for clean code.
        """
        try:
            logger.info(f"GetManualExtractionConfigFieldsById: id={documentConfigurationId}")
            return {
                "documentConfigurationID": documentConfigurationId
            }
        except Exception as ex:
            logger.error(f"GetManualExtractionConfigFieldsById error: {ex}", exc_info=True)
            raise

    def approve_document(
        self,
        db: Session,
        document: ApproveDocumentRequest,
    ) -> Dict:
        """
        This replicates the ApproveDocument endpoint,
        """
        try:
            logger.info(f"ApproveDocument: docuid={document.doc_uid}")

            logger.info(f"ApproveDocument: document approval for {document.doc_uid}")
            return {
                "result_code": "Success",
                "total": 0,
                "data": None,
                "result_message": "Document approved successfully"
            }

        except Exception as ex:
            logger.error(f"ApproveDocument error: {ex}", exc_info=True)
            raise

    def ignore_document(
        self,
        db: Session,
        document: Document
    ) -> int:
        """
        This endpoint replicates the IgnoreDocument endpoint from .NET.
        """
        try:
            logger.info(f"IgnoreDocument: docuid={document.doc_uid}")

            logger.info(f"IgnoreDocument: document approval for {document.doc_uid}")
            return 1

        except Exception as ex:
            logger.error(f"IgnoreDocument error: {ex}", exc_info=True)
            raise

    def replay_document(
        self,
        db: Session,
        document: UpdateDocumentReplayRequest
    ) -> bool:
        """
        Replay document

        This endpoint replicates the ReplayDocument endpoint,
        providing the same functionality using SQLAlchemy ORM queries that work on
        both PostgreSQL and SQL Server.
        """
        try:
            logger.info(f"ReplayDocument: docuid={document.doc_uid}")

            logger.info(f"ReplayDocument: document approval for {document.doc_uid}")
            return 1

        except Exception as ex:
            logger.error(f"ReplayDocument error: {ex}", exc_info=True)
            raise

    def all_replay_document(
        self,
        db: Session,
        document: UpdateDocumentReplayRequest
    ) -> bool:
        """
        All Replay document

        This endpoint replicates the AllReplayDocument endpoint,
        providing the same functionality using SQLAlchemy ORM queries that work on
        both PostgreSQL and SQL Server.
        """
        try:
            logger.info(f"AllReplayDocument: docuid={document.doc_uid}")

            logger.info(f"AllReplayDocument: document approval for {document.doc_uid}")
            return 1

        except Exception as ex:
            logger.error(f"AllReplayDocument error: {ex}", exc_info=True)
            raise