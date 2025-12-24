"""
Document Manager Result Enricher
Handles post-query enrichment: account info, SLA calculations, ingestion counts.
"""
from datetime import datetime
from typing import List, Dict
from uuid import UUID

from sqlalchemy import func, cast, String
from sqlalchemy.orm import Session

from src.domain.dtos.document_manager_dto import DocumentManagerFilter, DocumentManagerItem
from src.domain.entities.file_manager import FileManager
from src.domain.entities.extract_file import ExtractFile
from src.domain.entities.account_master import AccountMaster
from src.domain.entities.file_configuration import FileConfiguration
from src.domain.entities.firm_master import FirmMaster


class DocumentManagerResultEnricher:
    """
    Enriches query results with:
    - Account info from ExtractFile + AccountMaster joins
    - SLA calculations (Age, SLADays, SLAStatus, TSLAStatus)
    - Ingestion counts
    """
    
    def __init__(self, db: Session, filters: DocumentManagerFilter):
        self.db = db
        self.filters = filters
        self._config_map = None
    
    def enrich(self, results: List[FileManager]) -> List[Dict]:
        """Enrich results with account info and SLA calculations."""
        if not results:
            return []
        
        doc_uids = [r.fileuid for r in results]
        
        # Load lookup data
        self._config_map = self._get_configuration_map()
        account_info = self._get_account_info(doc_uids)
        business_dates = self._get_business_dates(doc_uids)
        ingestion_counts = self._get_ingestion_counts(doc_uids)
        
        # Build enriched items
        items = []
        for doc in results:
            item = self._build_item(doc, account_info, business_dates, ingestion_counts)
            items.append(item)
        
        return items
    
    def _build_item(
        self, 
        doc: FileManager, 
        account_info: Dict, 
        business_dates: Dict,
        ingestion_counts: Dict
    ) -> Dict:
        """Build a single enriched item."""
        # Get SLA info
        config_name = (
            doc.filetypegenai 
            if doc.status in ['Linked', 'Approved', 'Ingested', 'Completed', 'Ignored']
            else doc.filetypeproceesrule
        )
        sla_days = self._config_map.get(config_name, 0)
        
        # Calculate age
        age = doc.age or 0
        if doc.created:
            age = (datetime.utcnow() - doc.created).days
        
        # Calculate SLA status
        age_sla_display, sla_status = self._calculate_sla_status(age, sla_days)
        tsla_status = self._calculate_tsla_status(age)
        
        # Get account and ingestion info
        doc_key = str(doc.fileuid)
        acct = account_info.get(doc_key, {})
        ingestion = ingestion_counts.get(doc_key, {})
        
        item = DocumentManagerItem(
            total_count=0,
            id=doc.fileid,
            status=doc.status,
            status_date=doc.statusdate,
            type=doc.type,
            ignored_on=doc.ignoredon,
            ignored_by=doc.ignoredby,
            rule=doc.rule,
            document_name=doc.filename,
            failure_stage=doc.failurestage,
            reason=doc.reason,
            age=age,
            sla_days=sla_days,
            harvest_source=doc.harvestsource,
            document_type_procees_rule=doc.filetypeproceesrule,
            document_type_gen_ai=doc.filetypegenai,
            processing_method=doc.method,
            capture_method=doc.capturemethod,
            # capture_system=doc.capture_system,
            email_sender=doc.emailsender,
            email_subject=doc.emailsubject,
            linking_method=doc.linkingmethod,
            # linking_system=doc.linking_system,
            extract_method=doc.extractmethod,
            extract_system=doc.extractsystem,
            batch=doc.batchid,
            # source_attributes=doc.source_attributes,
            doc_uid=doc.fileuid,
            duplicate_document_id=doc.duplicatefileid,
            stage=doc.stage,
            metadata=doc.file_metadata,
            business_rule_applied_date=doc.businessruleapplieddate,
            file_type=doc.fileextension,
            created=doc.created,
            created_by=doc.createdby,
            category=doc.category,
            status_comment=doc.statuscomment,
            age_sla_display=age_sla_display,
            sla_status=sla_status,
            tsla_status=tsla_status,
            # Account info
            firm_name=acct.get('firm_name'),
            firm_id=acct.get('firm_id'),
            entity_name=acct.get('entity_name'),
            account_name=acct.get('account_name'),
            account_sid=acct.get('account_sid'),
            account_uid=acct.get('account_uid'),
            investor=acct.get('investor'),
            business_date=business_dates.get(doc_key),
            is_core_account=acct.get('is_core_account', False),
            # Ingestion counts
            ingestion_in_progress_count=ingestion.get('in_progress', 0),
            ingestion_failed_count=ingestion.get('failed', 0),
            manual_ingested_count=ingestion.get('manual', 0),
            ingestion_done_count=ingestion.get('done', 0),
            total_ingestion_count=ingestion.get('total', 0),
        )
        return item.model_dump()
    
    def _calculate_sla_status(self, age: int, sla_days: int) -> tuple:
        """Calculate SLA status and display string."""
        if sla_days and sla_days > 0:
            if age < sla_days:
                sla_status = "Within SLA"
            elif age == sla_days:
                sla_status = "On SLA"
            else:
                sla_status = "SLA Breached"
            age_sla_display = f"{age}/{sla_days}"
        else:
            sla_status = None
            age_sla_display = str(age)
        return age_sla_display, sla_status
    
    def _calculate_tsla_status(self, age: int) -> str:
        """Calculate TSLA status."""
        if age == 0:
            return "T0"
        elif age == 1:
            return "T1"
        elif age == 2:
            return "T2"
        elif age == 3:
            return "T3"
        elif age > 3:
            return "T3+"
        return None
    
    # =========================================================================
    # DATA LOADERS
    # =========================================================================
    
    def _get_configuration_map(self) -> Dict[str, int]:
        """Get mapping of configuration_name -> sla_days."""
        configs = self.db.query(
            FileConfiguration.configuration_name,
            FileConfiguration.sla_days
        ).filter(
            FileConfiguration.isactive == True,
            FileConfiguration.sla_days.isnot(None)
        ).all()
        return {c.configuration_name: c.sla_days for c in configs}
    
    def _get_account_info(self, doc_uids: List[UUID]) -> Dict[str, Dict]:
        """Get account information with aggregation."""
        query = self.db.query(
            ExtractFile.fileuid,
            AccountMaster.firm_name,
            AccountMaster.firm_id,
            AccountMaster.entity_name,
            AccountMaster.account_name,
            AccountMaster.tokenized_account_name,
            AccountMaster.accounts_id.label('account_sid'),
            AccountMaster.account_uid,
            AccountMaster.investor,
            AccountMaster.tokenized_investor,
            FirmMaster.system.label('firm_system')
        ).join(
            AccountMaster, ExtractFile.account_uid == AccountMaster.account_uid
        ).outerjoin(
            FirmMaster, AccountMaster.firm_id == FirmMaster.firm_id
        ).filter(
            ExtractFile.fileuid.in_(doc_uids),
            ExtractFile.isactive == True,
            ExtractFile.islinked == True,
            AccountMaster.isactive == True
        ).all()
        
        return self._aggregate_account_info(query)
    
    def _aggregate_account_info(self, query_results) -> Dict[str, Dict]:
        """Aggregate account info by doc_uid."""
        result = {}
        visibility = self.filters.visibility
        
        for row in query_results:
            doc_key = str(row.doc_uid)
            if doc_key not in result:
                result[doc_key] = {
                    'firm_name': [], 'firm_id': [], 'entity_name': [],
                    'account_name': [], 'account_sid': [], 'account_uid': [],
                    'investor': [], 'is_core_account': False
                }
            
            r = result[doc_key]
            if row.firm_name: r['firm_name'].append(row.firm_name)
            if row.firm_id: r['firm_id'].append(str(row.firm_id))
            if row.entity_name: r['entity_name'].append(row.entity_name)
            
            # Use tokenized values based on visibility
            if visibility == 'S':
                if row.tokenized_account_name: r['account_name'].append(row.tokenized_account_name)
                if row.tokenized_investor: r['investor'].append(row.tokenized_investor)
            else:
                if row.account_name: r['account_name'].append(row.account_name)
                if row.investor: r['investor'].append(row.investor)
            
            if row.account_sid: r['account_sid'].append(row.account_sid)
            if row.account_uid: r['account_uid'].append(str(row.account_uid))
            if row.firm_system == 'Core': r['is_core_account'] = True
        
        # Convert lists to comma-separated strings
        for doc_key in result:
            for field in ['firm_name', 'firm_id', 'entity_name', 'account_name', 'account_sid', 'account_uid', 'investor']:
                values = list(set(result[doc_key][field]))
                result[doc_key][field] = ', '.join(values) if values else None
        
        return result
    
    def _get_business_dates(self, doc_uids: List[UUID]) -> Dict[str, str]:
        """Get aggregated business dates."""
        from sqlalchemy import literal
        query = self.db.query(
            ExtractFile.fileuid,
            func.string_agg(
                cast(ExtractFile.businessdate, String), 
                literal(', ', type_=String(5))
            ).label('dates')
        ).filter(
            ExtractFile.fileuid.in_(doc_uids),
            ExtractFile.isactive == True
        ).group_by(ExtractFile.fileuid).all()
        return {str(row.fileuid): row.dates for row in query}
    
    def _get_ingestion_counts(self, doc_uids: List[UUID]) -> Dict[str, Dict]:
        """Get ingestion status counts."""
        query = self.db.query(
            ExtractFile.fileuid,
            ExtractFile.ingestionstatus,
            ExtractFile.ismanualingested,
            func.count().label('cnt')
        ).filter(
            ExtractFile.fileuid.in_(doc_uids),
            ExtractFile.isactive == True
        ).group_by(
            ExtractFile.fileuid,
            ExtractFile.ingestionstatus,
            ExtractFile.ismanualingested
        ).all()
        
        result = {}
        for row in query:
            doc_key = str(row.fileuid)
            if doc_key not in result:
                result[doc_key] = {'in_progress': 0, 'failed': 0, 'manual': 0, 'done': 0, 'total': 0}
            
            status = (row.ingestionstatus or '').lower().strip()
            r = result[doc_key]
            
            if status in ['in progress', 'inprogress', '']:
                r['in_progress'] += row.cnt
            elif status == 'failed':
                r['failed'] += row.cnt
            elif status == 'success':
                if row.ismanualingested:
                    r['manual'] += row.cnt
                else:
                    r['done'] += row.cnt
            
            r['total'] = r['in_progress'] + r['failed'] + r['manual'] + r['done']
        
        return result
