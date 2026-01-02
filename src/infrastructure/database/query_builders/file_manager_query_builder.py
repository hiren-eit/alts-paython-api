"""
File Manager Query Builder
Separates the query building logic from the repository for cleaner architecture.
This module handles all filter, sorting, and join logic for GetFileManager.
"""

from datetime import datetime
from typing import List, Dict, Optional
from uuid import UUID

from sqlalchemy import func, and_, or_, cast, String
from sqlalchemy.orm import Session, aliased

from src.domain.dtos.file_manager_dto import FileManagerFilter
from src.domain.entities.file_manager import FileManager
from src.domain.entities.extract_file import ExtractFile
from src.domain.entities.account_master import AccountMaster
from src.domain.entities.file_configuration import FileConfiguration
from src.domain.entities.firm_master import FirmMaster


class FileManagerQueryBuilder:
    """
    Query builder for GetFileManager.
    Encapsulates all filtering, sorting, and join logic.
    """

    def __init__(self, db: Session, filters: FileManagerFilter):
        self.db = db
        self.filters = filters
        self._query = None

    def build_query(self):
        """Build the complete query with all filters applied."""
        self._query = self._build_base_query()
        self._query = self._apply_status_filter()
        self._query = self._apply_sla_filter()
        self._query = self._apply_user_filters()
        return self

    def get_count(self) -> int:
        """Get total count before pagination."""
        return self._query.count()

    def get_results(self) -> List:
        """Get paginated results."""
        query = self._apply_sorting()
        offset = (self.filters.page_number - 1) * self.filters.page_size
        return query.offset(offset).limit(self.filters.page_size).all()

    # =========================================================================
    # BASE QUERY
    # =========================================================================

    def _build_base_query(self):
        """Build the base query with FileManager entity."""
        query = self.db.query(FileManager).filter(
            FileManager.isactive == True,
            ~FileManager.stage.in_(["DocReady", "DocReady1"]),
        )

        # If business date or firm filters exist, use subquery filter
        if self._needs_extract_filter():
            extract_subquery = self._build_extract_subquery()
            query = query.filter(FileManager.fileuid.in_(extract_subquery))

        return query

    def _needs_extract_filter(self) -> bool:
        """Check if we need to filter via ExtractFile."""
        return (
            self.filters.filter_business_date_from is not None
            or self.filters.filter_business_date_to is not None
            or self.filters.firm_ids is not None
            or self.filters.account_sids is not None
            or self.filters.account_uids is not None
            or self.filters.investors is not None
            or self.filters.account_names is not None
            or self.filters.investor is not None
            or self.filters.account_name is not None
            or self.filters.entity_ids is not None
        )

    def _build_extract_subquery(self):
        """Build subquery for ExtractFile-based filters."""
        subquery = self.db.query(ExtractFile.fileuid).filter(
            ExtractFile.isactive == True,
            ExtractFile.islinked == True,
            ExtractFile.isignored == False,
        )

        if self.filters.filter_business_date_from:
            subquery = subquery.filter(
                ExtractFile.businessdate >= self.filters.filter_business_date_from
            )

        if self.filters.filter_business_date_to:
            subquery = subquery.filter(
                ExtractFile.businessdate < self.filters.filter_business_date_to
            )

        if self.filters.firm_ids:
            subquery = subquery.filter(ExtractFile.firm_id.in_(self.filters.firm_ids))

        if self.filters.account_sids:
            subquery = subquery.filter(ExtractFile.account_sid.in_(self.filters.account_sids))

        if self.filters.account_uids:
            subquery = subquery.filter(cast(ExtractFile.account_uid, String).in_(self.filters.account_uids))

        if self.filters.entity_ids:
            subquery = subquery.filter(cast(ExtractFile.entity_uid, String).in_(self.filters.entity_ids))

        if self.filters.investors or self.filters.account_names or self.filters.investor or self.filters.account_name:
            subquery = subquery.outerjoin(
                AccountMaster, 
                (ExtractFile.account_uid == AccountMaster.account_uid) & 
                (AccountMaster.isactive == True)
            )
            if self.filters.investors or self.filters.investor:
                investors = self.filters.investors or []
                if self.filters.investor: investors.append(self.filters.investor)
                
                if self.filters.visibility == 'S':
                    # Tokenized mode: Only match tokenized field
                    subquery = subquery.filter(AccountMaster.tokenized_investor.in_(investors))
                else:
                    # Detokenized/Normal mode (D): Match ExtractFile or AccountMaster names
                    subquery = subquery.filter(
                        or_(
                            ExtractFile.investor.in_(investors),
                            AccountMaster.investor.in_(investors)
                        )
                    )
                    
            if self.filters.account_names or self.filters.account_name:
                names = self.filters.account_names or []
                if self.filters.account_name: names.append(self.filters.account_name)
                
                if self.filters.visibility == 'S':
                    # Tokenized mode: Only match tokenized field
                    subquery = subquery.filter(AccountMaster.tokenized_account_name.in_(names))
                else:
                    # Detokenized/Normal mode (D): Match ExtractFile or AccountMaster names
                    subquery = subquery.filter(
                        or_(
                            ExtractFile.account.in_(names),
                            AccountMaster.account_name.in_(names)
                        )
                    )

        return subquery

    # =========================================================================
    # STATUS FILTER (Tab Filter)
    # =========================================================================

    def _apply_status_filter(self):
        """Apply file status filter based on the tab selected."""
        query = self._query
        file_type = self.filters.file_type
        status = self.filters.file_status.lower()

        status_handlers = {
            "all": self._filter_all,
            "approved": self._filter_approved,
            "captured": self._filter_captured,
            "toreview": self._filter_to_review,
            "extracted": self._filter_extracted,
            "ignored": self._filter_ignored,
            "linked": self._filter_linked,
            "ingested": self._filter_ingested,
            "duplicates": self._filter_duplicates,
            "completed": self._filter_completed,
            "inprogress": self._filter_in_progress,
        }

        handler = status_handlers.get(status)
        if handler:
            query = handler(query, file_type)

        return query

    def _filter_all(self, query, file_type):
        query = query.filter(
            or_(
                and_(
                    FileManager.status == "Failed",
                    FileManager.failurestage.in_(
                        ["Failed Capture", "Failed Extraction", "Failed Linking"]
                    ),
                ),
                FileManager.status.in_(["Captured", "Extract", "Update", "Pending"]),
            )
        )
        if file_type != "All":
            query = query.filter(FileManager.filetypeproceesrule == file_type)
        return query

    def _filter_approved(self, query, file_type):
        query = query.filter(FileManager.status == "Approved")
        if file_type != "All":
            query = query.filter(FileManager.filetypegenai == file_type)
        return query

    def _filter_captured(self, query, file_type):
        query = query.filter(
            FileManager.status == "Failed", FileManager.failurestage == "Failed Capture"
        )
        if file_type != "All":
            query = query.filter(FileManager.filetypeproceesrule == file_type)
        return query

    def _filter_to_review(self, query, file_type):
        query = query.filter(
            FileManager.status == "Linked", FileManager.stage != "Completed"
        )
        if file_type != "All":
            query = query.filter(FileManager.filetypegenai == file_type)
        return query

    def _filter_extracted(self, query, file_type):
        query = query.filter(
            FileManager.status == "Failed",
            FileManager.failurestage == "Failed Extraction",
        )
        if file_type != "All":
            query = query.filter(FileManager.filetypeproceesrule == file_type)
        return query

    def _filter_ignored(self, query, file_type):
        query = query.filter(FileManager.status == "Ignored")
        if file_type != "All":
            query = query.filter(FileManager.filetypeproceesrule == file_type)
        return query

    def _filter_linked(self, query, file_type):
        query = query.filter(
            FileManager.status == "Failed", FileManager.failurestage == "Failed Linking"
        )
        if file_type != "All":
            query = query.filter(FileManager.filetypeproceesrule == file_type)
        return query

    def _filter_ingested(self, query, file_type):
        query = query.filter(
            FileManager.status == "Failed",
            FileManager.failurestage == "Failed Ingestion",
        )
        if file_type != "All":
            query = query.filter(FileManager.filetypeproceesrule == file_type)
        return query

    def _filter_duplicates(self, query, file_type):
        query = query.filter(FileManager.status == "duplicate")
        if file_type != "All":
            query = query.filter(FileManager.filetypegenai == file_type)
        return query

    def _filter_completed(self, query, file_type):
        query = query.filter(
            or_(
                FileManager.status.in_(["ingested", "Hub Persisted", "Completed"]),
                and_(
                    FileManager.status == "Linked",
                    FileManager.stage == "Completed",
                    FileManager.method.in_(["HAAS", "AUTOMATED"]),
                ),
            )
        )
        if file_type != "All":
            query = query.filter(FileManager.filetypegenai == file_type)
        return query

    def _filter_in_progress(self, query, file_type):
        query = query.filter(
            FileManager.status.in_(["Captured", "Extract", "Update", "Pending"]),
            FileManager.stage.in_(
                [
                    "ExtractReady",
                    "ExtractSend",
                    "AccountLinkage",
                    "AccountLinkageFailed",
                    "ExtractReceived",
                    "ExtractFailed",
                    "Manual",
                    "AccountIdentification",
                ]
            ),
        )
        if file_type != "All":
            query = query.filter(FileManager.filetypeproceesrule == file_type)
        return query

    # =========================================================================
    # SLA FILTER
    # =========================================================================

    def _apply_sla_filter(self):
        """Apply SLA type filter."""
        query = self._query
        sla_type = self.filters.sla_type.lower()

        if sla_type == "all":
            return query

        # Join FileConfiguration based on status logic (matches SP)
        # We need to calculate age in days: (current_date - createdate)
        today = datetime.utcnow()
        age_expr = func.extract('day', today - FileManager.createdate)

        # SP Join logic:
        # LEFT JOIN [alts].[DocumentConfiguration] DC 
        # ON (
        #     (D.Status IN ('Captured', 'Extract', 'Update', 'Failed') AND DC.ConfigurationName = D.DocumentTypeProceesRule)
        #     OR ((D.Status IN ('Linked', 'Approved', 'Ingested', 'Completed', 'Ignored') OR (D.Status = 'Failed' AND D.FailureStage = 'Failed Ingestion')) AND DC.ConfigurationName = D.DocumentTypeGenAI)
        # )
        
        # In SQLAlchemy, we use an outer join to avoid filtering out records if SLA type is NOT 'uncategorized'
        # But for specific SLA filters, it's effectively an inner join.
        
        query = query.outerjoin(
            FileConfiguration,
            or_(
                and_(
                    FileManager.status.in_(["Captured", "Extract", "Update", "Failed", "Pending"]),
                    FileConfiguration.configurationname == FileManager.filetypeprocessrule
                ),
                and_(
                    or_(
                        FileManager.status.in_(["Linked", "Approved", "Ingested", "Completed", "Ignored"]),
                        and_(FileManager.status == "Failed", FileManager.failurestage == "Failed Ingestion")
                    ),
                    FileConfiguration.configurationname == FileManager.filetypegenai
                )
            )
        )

        if sla_type == "withinsla":
            query = query.filter(
                and_(
                    age_expr < FileConfiguration.sla_days,
                    FileConfiguration.sla_days.isnot(None)
                )
            )
        elif sla_type == "onsla":
            query = query.filter(
                and_(
                    age_expr == FileConfiguration.sla_days,
                    FileConfiguration.sla_days.isnot(None),
                    age_expr != 0,
                    FileConfiguration.sla_days != 0
                )
            )
        elif sla_type == "slabreached":
            query = query.filter(
                and_(
                    age_expr > FileConfiguration.sla_days,
                    FileConfiguration.sla_days.isnot(None)
                )
            )
        elif sla_type == "uncategorized":
            query = query.filter(FileConfiguration.sla_days.is_None())

        return query

    # =========================================================================
    # USER FILTERS
    # =========================================================================

    def _apply_user_filters(self):
        """Apply all user-provided filters."""
        query = self._query
        f = self.filters

        # Search text
        if f.search_text:
            search_conditions = []
            for text in f.search_text:
                pattern = f"%{text}%"
                
                # FileManager fields
                fm_cond = or_(
                    FileManager.filename.ilike(pattern),
                    cast(FileManager.fileuid, String).ilike(pattern),
                    cast(FileManager.entityuid, String).ilike(pattern),
                    cast(FileManager.firm, String).ilike(pattern),
                    FileManager.emailsender.ilike(pattern),
                    FileManager.batchid.ilike(pattern),
                    FileManager.file_metadata.ilike(pattern),
                )
                
                # ExtractFile/AccountMaster fields
                if f.visibility == "S":
                    extract_filters = [
                        ExtractFile.account_sid.ilike(pattern),
                        AccountMaster.tokenized_investor.ilike(pattern),
                        AccountMaster.tokenized_account_name.ilike(pattern),
                        AccountMaster.entity_name.ilike(pattern),
                    ]
                else:
                    extract_filters = [
                        ExtractFile.account_sid.ilike(pattern),
                        ExtractFile.investor.ilike(pattern),
                        ExtractFile.account.ilike(pattern),
                        AccountMaster.investor.ilike(pattern),
                        AccountMaster.account_name.ilike(pattern),
                        AccountMaster.entity_name.ilike(pattern),
                    ]

                extract_exists = (
                    self.db.query(ExtractFile.fileuid)
                    .outerjoin(AccountMaster, (ExtractFile.account_uid == AccountMaster.account_uid) & (AccountMaster.isactive == True))
                    .filter(
                        ExtractFile.fileuid == FileManager.fileuid,
                        ExtractFile.isactive == True,
                        or_(*extract_filters),
                    )
                    .exists()
                )

                search_conditions.append(or_(fm_cond, extract_exists))
            
            if search_conditions:
                query = query.filter(or_(*search_conditions))

        # List filters
        list_filters = [
            (f.file_types, FileManager.fileextension),
            (f.file_type_gen_ai, FileManager.filetypegenai),
            (f.file_type_procees_rule, FileManager.filetypeprocessrule),
            (f.status_comments, FileManager.statuscomment),
            (f.failure_stages, FileManager.failurestage),
            (f.reasons, FileManager.reason),
            (f.last_stages, FileManager.stage),
            (f.processing_methods, FileManager.method),
            (f.capture_methods, FileManager.capturemethod),
            # (f.capture_systems, FileManager.capturesystem),
            (f.extract_methods, FileManager.extractmethod),
            (f.extract_systems, FileManager.extractsystem),
            (f.senders, FileManager.emailsender),
            (f.subjects, FileManager.emailsubject),
            (f.ignored_by, FileManager.ignoredby),
            (f.firm_ids, FileManager.firm),
        ]

        for values, column in list_filters:
            if values:
                query = query.filter(column.in_(values))

        # UUID list filters (need cast if filtering with strings)
        if f.entity_ids:
            query = query.filter(cast(FileManager.entityuid, String).in_(f.entity_ids))

        if f.entity_uid:
            query = query.filter(cast(FileManager.entityuid, String) == f.entity_uid)

        # FileUID filter (needs cast)
        if f.file_uids:
            query = query.filter(cast(FileManager.fileuid, String).in_(f.file_uids))

        # Single value filters
        single_filters = [
            (f.source, FileManager.harvestsource),
            (f.linking_method, FileManager.linkingmethod),
            (f.batch_id, FileManager.batchid),
        ]

        for value, column in single_filters:
            if value:
                query = query.filter(column == value)

        if f.firm_id:
            query = query.filter(FileManager.firm == f.firm_id)

        # Date range filters
        if f.filter_created_date_from:
            query = query.filter(
                func.date(FileManager.createdate) >= f.filter_created_date_from
            )
        if f.filter_created_date_to:
            query = query.filter(
                func.date(FileManager.createdate) <= f.filter_created_date_to
            )
        if f.filter_status_date_from:
            query = query.filter(
                func.date(FileManager.statusdate) >= f.filter_status_date_from
            )
        if f.filter_status_date_to:
            query = query.filter(
                func.date(FileManager.statusdate) <= f.filter_status_date_to
            )

        return query

    # =========================================================================
    # SORTING
    # =========================================================================

    def _apply_sorting(self):
        """Apply dynamic sorting."""
        query = self._query
        sort_column = self.filters.sort_column
        sort_order = (self.filters.sort_order or "desc").lower()

        if not sort_column:
            return query.order_by(FileManager.statusdate.desc())

        column_map = {
            "status": FileManager.status,
            "statusdate": FileManager.statusdate,
            "status_date": FileManager.statusdate,
            "filetype": FileManager.fileextension,
            "file_type": FileManager.fileextension,
            "ignoredon": FileManager.ignoredon,
            "ignored_on": FileManager.ignoredon,
            "ignoredby": FileManager.ignoredby,
            "ignored_by": FileManager.ignoredby,
            "rule": FileManager.rule,
            "filename": FileManager.filename,
            "file_name": FileManager.filename,
            "reason": FileManager.reason,
            "age": FileManager.age,
            "harvestsource": FileManager.harvestsource,
            "harvest_source": FileManager.harvestsource,
            "filetypeprocesrule": FileManager.filetypeprocessrule,
            "filetypegenai": FileManager.filetypegenai,
            "processingmethod": FileManager.method,
            "capturemethod": FileManager.capturemethod,
            # 'capturesystem': FileManager.capturesystem,
            "emailsender": FileManager.emailsender,
            "emailsubject": FileManager.emailsubject,
            "linkingmethod": FileManager.linkingmethod,
            # 'linkingsystem': FileManager.linkingsystem,
            "extractmethod": FileManager.extractmethod,
            "extractsystem": FileManager.extractsystem,
            "batch": FileManager.batchid,
            # 'sourceattributes': FileManager.sourceattributes,
            "fileuid": FileManager.fileuid,
            "stage": FileManager.stage,
            "created": FileManager.createdate,
            "createdby": FileManager.createby,
            "category": FileManager.category,
        }

        column = column_map.get(sort_column.lower(), FileManager.createdate)

        if sort_order == "asc":
            return query.order_by(column.asc())
        return query.order_by(column.desc())
