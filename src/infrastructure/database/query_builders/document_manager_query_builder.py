"""
Document Manager Query Builder
Separates the query building logic from the repository for cleaner architecture.
This module handles all filter, sorting, and join logic for GetDocumentManager.
"""
from datetime import datetime
from typing import List, Dict, Optional
from uuid import UUID

from sqlalchemy import func, and_, or_, cast, String
from sqlalchemy.orm import Session, aliased

from src.domain.dtos.document_manager_dto import DocumentManagerFilter
from src.domain.entities.file_manager import FileManager
from src.domain.entities.extract_file import ExtractFile
from src.domain.entities.account_master import AccountMaster
from src.domain.entities.file_configuration import FileConfiguration
from src.domain.entities.firm_master import FirmMaster


class DocumentManagerQueryBuilder:
    """
    Query builder for GetDocumentManager.
    Encapsulates all filtering, sorting, and join logic.
    """
    
    def __init__(self, db: Session, filters: DocumentManagerFilter):
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
            ~FileManager.stage.in_(['DocReady', 'DocReady1'])
        )
        
        # If business date or firm filters exist, use subquery filter
        if self._needs_extract_filter():
            extract_subquery = self._build_extract_subquery()
            query = query.filter(FileManager.fileuid.in_(extract_subquery))
        
        return query
    
    def _needs_extract_filter(self) -> bool:
        """Check if we need to filter via ExtractFile."""
        return (
            self.filters.filter_business_date_from is not None or
            self.filters.filter_business_date_to is not None or
            self.filters.firm_ids is not None
        )
    
    def _build_extract_subquery(self):
        """Build subquery for ExtractFile-based filters."""
        subquery = self.db.query(ExtractFile.doc_uid).filter(
            ExtractFile.isactive == True,
            ExtractFile.islinked == True,
            ExtractFile.isignored == False
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
            subquery = subquery.join(
                AccountMaster, ExtractFile.account_uid == AccountMaster.account_uid
            ).filter(
                AccountMaster.firm_id.in_(self.filters.firm_ids),
                AccountMaster.isactive == True
            )
        
        return subquery
    
    # =========================================================================
    # STATUS FILTER (Tab Filter)
    # =========================================================================
    
    def _apply_status_filter(self):
        """Apply document status filter based on the tab selected."""
        query = self._query
        doc_type = self.filters.doc_type
        status = self.filters.document_status.lower()
        
        status_handlers = {
            'all': self._filter_all,
            'approved': self._filter_approved,
            'captured': self._filter_captured,
            'toreview': self._filter_to_review,
            'extracted': self._filter_extracted,
            'ignored': self._filter_ignored,
            'linked': self._filter_linked,
            'ingested': self._filter_ingested,
            'duplicates': self._filter_duplicates,
            'completed': self._filter_completed,
            'inprogress': self._filter_in_progress,
        }
        
        handler = status_handlers.get(status)
        if handler:
            query = handler(query, doc_type)
        
        return query
    
    def _filter_all(self, query, doc_type):
        query = query.filter(
            or_(
                and_(
                    FileManager.status == 'Failed',
                    FileManager.failurestage.in_(['Failed Capture', 'Failed Extraction', 'Failed Linking'])
                ),
                FileManager.status.in_(['Captured', 'Extract', 'Update', 'Pending'])
            )
        )
        if doc_type != 'All':
            query = query.filter(FileManager.filetypeproceesrule == doc_type)
        return query
    
    def _filter_approved(self, query, doc_type):
        query = query.filter(FileManager.status == 'Approved')
        if doc_type != 'All':
            query = query.filter(FileManager.filetypegenai == doc_type)
        return query
    
    def _filter_captured(self, query, doc_type):
        query = query.filter(
            FileManager.status == 'Failed',
            FileManager.failurestage == 'Failed Capture'
        )
        if doc_type != 'All':
            query = query.filter(FileManager.filetypeproceesrule == doc_type)
        return query
    
    def _filter_to_review(self, query, doc_type):
        query = query.filter(
            FileManager.status == 'Linked',
            FileManager.stage != 'Completed'
        )
        if doc_type != 'All':
            query = query.filter(FileManager.filetypegenai == doc_type)
        return query
    
    def _filter_extracted(self, query, doc_type):
        query = query.filter(
            FileManager.status == 'Failed',
            FileManager.failurestage == 'Failed Extraction'
        )
        if doc_type != 'All':
            query = query.filter(FileManager.filetypeproceesrule == doc_type)
        return query
    
    def _filter_ignored(self, query, doc_type):
        query = query.filter(FileManager.status == 'Ignored')
        if doc_type != 'All':
            query = query.filter(FileManager.filetypeproceesrule == doc_type)
        return query
    
    def _filter_linked(self, query, doc_type):
        query = query.filter(
            FileManager.status == 'Failed',
            FileManager.failurestage == 'Failed Linking'
        )
        if doc_type != 'All':
            query = query.filter(FileManager.filetypeproceesrule == doc_type)
        return query
    
    def _filter_ingested(self, query, doc_type):
        query = query.filter(
            FileManager.status == 'Failed',
            FileManager.failurestage == 'Failed Ingestion'
        )
        if doc_type != 'All':
            query = query.filter(FileManager.filetypeproceesrule == doc_type)
        return query
    
    def _filter_duplicates(self, query, doc_type):
        query = query.filter(FileManager.status == 'duplicate')
        if doc_type != 'All':
            query = query.filter(FileManager.document_type_gen_ai == doc_type)
        return query
    
    def _filter_completed(self, query, doc_type):
        query = query.filter(
            or_(
                FileManager.status.in_(['ingested', 'Hub Persisted', 'Completed']),
                and_(
                    FileManager.status == 'Linked',
                    FileManager.stage == 'Completed',
                    FileManager.method.in_(['HAAS', 'AUTOMATED'])
                )
            )
        )
        if doc_type != 'All':
            query = query.filter(FileManager.filetypegenai == doc_type)
        return query
    
    def _filter_in_progress(self, query, doc_type):
        query = query.filter(
            FileManager.status.in_(['Captured', 'Extract', 'Update', 'Pending']),
            FileManager.stage.in_([
                'ExtractReady', 'ExtractSend', 'AccountLinkage', 'AccountLinkageFailed',
                'ExtractReceived', 'ExtractFailed', 'Manual', 'AccountIdentification'
            ])
        )
        if doc_type != 'All':
            query = query.filter(FileManager.filetypeproceesrule == doc_type)
        return query
    
    # =========================================================================
    # SLA FILTER
    # =========================================================================
    
    def _apply_sla_filter(self):
        """Apply SLA type filter."""
        query = self._query
        sla_type = self.filters.sla_type.lower()
        
        if sla_type == 'all':
            pass  # No filter
        elif sla_type == 'withinsla':
            config_subquery = self.db.query(FileConfiguration.configuration_name).filter(
                FileConfiguration.sla_days.isnot(None)
            )
            query = query.filter(
                or_(
                    FileManager.filetypeproceesrule.in_(config_subquery),
                    FileManager.filetypegenai.in_(config_subquery)
                )
            )
        elif sla_type == 'uncategorized':
            config_names = self.db.query(FileConfiguration.configuration_name).filter(
                FileConfiguration.sla_days.isnot(None),
                FileConfiguration.isactive == True
            ).all()
            config_names = [c[0] for c in config_names]
            query = query.filter(
                ~FileManager.filetypeproceesrule.in_(config_names),
                ~FileManager.filetypegenai.in_(config_names)
            )
        
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
                search_conditions.append(
                    or_(
                        FileManager.filename.ilike(pattern),
                        cast(FileManager.fileuid, String).ilike(pattern),
                        FileManager.emailsubject.ilike(pattern),
                        FileManager.emailsender.ilike(pattern),
                        FileManager.batchid.ilike(pattern),
                        # FileManager.tag.ilike(pattern)
                    )
                )
            if search_conditions:
                query = query.filter(or_(*search_conditions))
        
        # List filters
        list_filters = [
            (f.file_types, FileManager.fileextension),
            (f.document_type_gen_ai, FileManager.filetypegenai),
            (f.document_type_procees_rule, FileManager.filetypeproceesrule),
            (f.status_comments, FileManager.statuscomment),
            (f.failure_stages, FileManager.failurestage),
            (f.reasons, FileManager.reason),
            (f.last_stages, FileManager.stage),
            (f.processing_methods, FileManager.method),
            (f.capture_methods, FileManager.capturemethod),
            # (f.capture_systems, FileManager.capture_system),
            (f.extract_methods, FileManager.extractmethod),
            (f.extract_systems, FileManager.extractsystem),
            (f.senders, FileManager.emailsender),
            (f.subjects, FileManager.emailsubject),
            (f.ignored_by, FileManager.ignoredby),
        ]
        
        for values, column in list_filters:
            if values:
                query = query.filter(column.in_(values))
        
        # DocUID filter (needs cast)
        if f.doc_uids:
            query = query.filter(cast(FileManager.fileuid, String).in_(f.doc_uids))
        
        # Single value filters
        single_filters = [
            (f.source, FileManager.harvestsource),
            (f.linking_method, FileManager.linkingmethod),
            (f.batch_id, FileManager.batchid),
        ]
        
        for value, column in single_filters:
            if value:
                query = query.filter(column == value)
        
        # Date range filters
        if f.filter_created_date_from:
            query = query.filter(func.date(FileManager.created) >= f.filter_created_date_from)
        if f.filter_created_date_to:
            query = query.filter(func.date(FileManager.created) <= f.filter_created_date_to)
        if f.filter_status_date_from:
            query = query.filter(func.date(FileManager.statusdate) >= f.filter_status_date_from)
        if f.filter_status_date_to:
            query = query.filter(func.date(FileManager.statusdate) <= f.filter_status_date_to)
        
        return query
    
    # =========================================================================
    # SORTING
    # =========================================================================
    
    def _apply_sorting(self):
        """Apply dynamic sorting."""
        query = self._query
        sort_column = self.filters.sort_column
        sort_order = (self.filters.sort_order or 'desc').lower()
        
        if not sort_column:
            return query.order_by(FileManager.statusdate.desc())
        
        column_map = {
            'status': FileManager.status,
            'statusdate': FileManager.statusdate,
            'status_date': FileManager.statusdate,
            'filetype': FileManager.fileextension,
            'file_type': FileManager.fileextension,
            'ignoredon': FileManager.ignoredon,
            'ignored_on': FileManager.ignoredon,
            'ignoredby': FileManager.ignoredby,
            'ignored_by': FileManager.ignoredby,
            'rule': FileManager.rule,
            'documentname': FileManager.filename,
            'document_name': FileManager.filename,
            'reason': FileManager.reason,
            'age': FileManager.age,
            'harvestsource': FileManager.harvestsource,
            'harvest_source': FileManager.harvestsource,
            'documenttypeprocesrule': FileManager.filetypeproceesrule,
            'documenttypegenai': FileManager.filetypegenai,
            'processingmethod': FileManager.method,
            'capturemethod': FileManager.capturemethod,
            # 'capturesystem': FileManager.capture_system,
            'emailsender': FileManager.emailsender,
            'emailsubject': FileManager.emailsubject,
            'linkingmethod': FileManager.linkingmethod,
            # 'linkingsystem': FileManager.linking_system,
            'extractmethod': FileManager.extractmethod,
            'extractsystem': FileManager.extractsystem,
            'batch': FileManager.batchid,
            # 'sourceattributes': FileManager.source_attributes,
            'docuid': FileManager.fileuid,
            'stage': FileManager.stage,
            'created': FileManager.created,
            'createdby': FileManager.createdby,
            'category': FileManager.category,
        }
        
        column = column_map.get(sort_column.lower(), FileManager.created)
        
        if sort_order == 'asc':
            return query.order_by(column.asc())
        return query.order_by(column.desc())
