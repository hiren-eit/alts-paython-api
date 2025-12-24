from typing import Optional, Dict, List
from datetime import datetime
from sqlalchemy import func, cast, String
from sqlalchemy.orm import Session
from uuid import UUID

from src.domain.dtos.document_details_dto import DocumentDetailsItem
from src.domain.entities.file_manager import FileManager
from src.domain.entities.extract_file import ExtractFile
from src.domain.entities.file_configuration import FileConfiguration
from src.domain.entities.account_master import AccountMaster

class DocumentDetailsResultEnricher:
    """
    Enriches file detail with:
    - Batch aggregation
    - Business dates
    - SLA calculation
    """

    def __init__(self, db: Session):
        self.db = db

    def enrich(self, result) -> Dict:
        doc, sla_days = result
        doc_uid = doc.fileuid

        batch = self._get_batches(doc_uid)
        business_date = self._get_business_dates(doc_uid)

        age = doc.age or 0
        age_sla_display, sla_status = self._calculate_sla(age, sla_days)

        return {
            "fileid": doc.fileid,
            "fileuid": doc.fileuid,
            "filename": doc.filename,
            "age": age,
            "ingestionfailedimageurl": doc.ingestionfailedimageurl,
            "metadata": doc.file_metadata,
            "category": doc.category,
            "sla_days": sla_days,
            "created": doc.created,
            "age_sla_display": age_sla_display,
            "status": doc.status,
            "stage": doc.stage,
            "failurestage": doc.failurestage,
            "statusdate": doc.statusdate,
            "harvestsource": doc.harvestsource,
            "method": doc.method,
            "batch": batch,
            "filetypeproceesrule": doc.filetypeproceesrule,
            "extractsystem": doc.extractsystem,
            "filetypegenai": doc.filetypegenai,
            "sla_status": sla_status,
            "businessdate": business_date,
        }

    # =========================================================================
    # SLA
    # =========================================================================

    def _calculate_sla(self, age: int, sla_days: int):
        if not sla_days:
            return str(age), None

        if age < sla_days:
            return f"{age}/{sla_days}", "Within SLA"
        if age == sla_days:
            return f"{age}/{sla_days}", "On SLA"
        return f"{age}/{sla_days}", "SLA Breached"

    # =========================================================================
    # AGGREGATIONS
    # =========================================================================

    def _get_batches(self, doc_uid: UUID) -> str:
        rows = (
            self.db.query(cast(ExtractFile.batchid, String))
            .filter(
                ExtractFile.fileuid == doc_uid,
                ExtractFile.isignored.is_(False)
            )
            .distinct()
            .all()
        )
        return ", ".join(r[0] for r in rows if r[0]) or None

    def _get_business_dates(self, doc_uid: UUID) -> str:
        rows = (
            self.db.query(cast(ExtractFile.businessdate, String))
            .filter(
                ExtractFile.fileuid == doc_uid,
                ExtractFile.isignored.is_(False)
            )
            .distinct()
            .all()
        )
        return ", ".join(r[0] for r in rows if r[0]) or None
