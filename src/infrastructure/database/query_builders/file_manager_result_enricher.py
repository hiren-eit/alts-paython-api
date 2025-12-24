"""
File Manager Result Enricher
Handles post-query mapping from entity to DTO.
"""
from datetime import datetime
from typing import List, Dict
from sqlalchemy.orm import Session

from src.domain.dtos.file_manager_dto import FileManagerFilter, DocumentManagerItem
from src.domain.entities.file_manager import FileManager
from src.domain.entities.file_configuration import FileConfiguration


class DocumentManagerResultEnricher:
    """
    Enriches query results by mapping FileManager entity to DocumentManagerItem DTO.
    """
    
    def __init__(self, db: Session, filters: FileManagerFilter):
        self.db = db
        self.filters = filters
        self._config_map = None
    
    
    def enrich(self, results: List[FileManager]) -> List[Dict]:
        """Enrich results by mapping entity to DTO and adding SLA info."""
        if not results:
            return []
        
        # Load SLA configuration mapping
        self._config_map = self._get_configuration_map()

        # Build enriched items
        items = []
        for doc in results:
            item = self._build_item(doc)
            items.append(item)
        
        return items
    
    def _build_item(self, doc: FileManager) -> Dict:
        """Build a single item mapping entity to DTO with SLA info."""
        # Get SLA info
        config_name = (
            doc.filetypegenai 
            if doc.status in ['Linked', 'Approved', 'Ingested', 'Completed', 'Ignored']
            else doc.filetypeproceesrule
        )
        sla_days = self._config_map.get(config_name, 0)

        # Calculate age
        age = doc.age or 0
        if doc.createdate:
            age = (datetime.utcnow() - doc.createdate.replace(tzinfo=None)).days
        
        # Calculate SLA status
        age_sla_display, sla_status = self._calculate_sla_status(age, sla_days)
        tsla_status = self._calculate_tsla_status(age)

        item = DocumentManagerItem(
            fileid=doc.fileid,
            fileuid=doc.fileuid,
            type=doc.type,
            filename=doc.filename,
            firm=doc.firm,
            entityuid=doc.entityuid,
            accountsid=doc.accountsid,
            accountuid=doc.accountuid,
            filepath=doc.filepath,
            createdate=doc.createdate,
            createtime=doc.createtime,
            comments=doc.comments,
            createby=str(doc.createby) if doc.createby is not None else None,
            filenameframe=doc.filenameframe,
            batchid=doc.batchid,
            metadata=doc.file_metadata,
            checksum=doc.checksum,
            status=doc.status,
            statusdate=doc.statusdate,
            method=doc.method,
            reasonid=doc.reasonid,
            reason=doc.reason,
            harvestsystem=doc.harvestsystem,
            harvestmethod=doc.harvestmethod,
            harvestsource=doc.harvestsource,
            indexsystem=doc.indexsystem,
            indexmethod=doc.indexmethod,
            extractsystem=doc.extractsystem,
            extractmethod=doc.extractmethod,
            age=age,
            emailsender=doc.emailsender,
            emailsubject=doc.emailsubject,
            category=doc.category,
            failurestage=doc.failurestage,
            filetypeproceesrule=doc.filetypeproceesrule,
            filetypegenai=doc.filetypegenai,
            ignoredon=doc.ignoredon,
            ignoredby=str(doc.ignoredby) if doc.ignoredby is not None else None,
            rule=doc.rule,
            businessdate=str(doc.businessdate.date()) if doc.businessdate else None,
            firmname=doc.firmname,
            entityname=doc.entityname,
            capturemethod=doc.capturemethod,
            linkingmethod=doc.linkingmethod,
            stage=doc.stage,
            isactive=doc.isactive,
            updatefileid=doc.updatefileid,
            statuscomment=doc.statuscomment,
            duplicatefileid=doc.duplicatefileid,
            fileprocessstage=doc.fileprocessstage,
            businessruleapplieddate=doc.businessruleapplieddate,
            fileextension=doc.fileextension,
            password=doc.password,
            groupcode=doc.groupcode,
            replay=doc.replay,
            lastattemptedtime=doc.lastattemptedtime,
            retrycount=doc.retrycount,
            ingestionfailedimageurl=doc.ingestionfailedimageurl,
            created=doc.created,
            createdby=str(doc.createdby) if doc.createdby is not None else None,
            updated=doc.updated,
            updatedby=str(doc.updatedby) if doc.updatedby is not None else None,
            age_sla_display=age_sla_display,
            sla_status=sla_status,
            tsla_status=tsla_status
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

    # =========================================================================
    # ARCHIVED METHODS (Commented out for future use)
    # =========================================================================
    
    # def _get_account_info(self, doc_uids: List[UUID]) -> Dict[str, Dict]:
    #     """Get account information with aggregation."""
    #     query = self.db.query(
    #         ExtractFile.fileuid,
    #         AccountMaster.firm_name,
    #         AccountMaster.firm_id,
    #         AccountMaster.entity_name,
    #         AccountMaster.account_name,
    #         AccountMaster.tokenized_account_name,
    #         AccountMaster.accounts_id.label('account_sid'),
    #         AccountMaster.account_uid,
    #         AccountMaster.investor,
    #         AccountMaster.tokenized_investor,
    #         FirmMaster.system.label('firm_system')
    #     ).join(
    #         AccountMaster, ExtractFile.account_uid == AccountMaster.account_uid
    #     ).outerjoin(
    #         FirmMaster, AccountMaster.firm_id == FirmMaster.firm_id
    #     ).filter(
    #         ExtractFile.fileuid.in_(doc_uids),
    #         ExtractFile.isactive == True,
    #         ExtractFile.islinked == True,
    #         AccountMaster.isactive == True
    #     ).all()
    #     return self._aggregate_account_info(query)
    
    # def _aggregate_account_info(self, query_results) -> Dict[str, Dict]:
    #     """Aggregate account info by doc_uid."""
    #     result = {}
    #     visibility = self.filters.visibility
    #     for row in query_results:
    #         doc_key = str(row.fileuid)
    #         if doc_key not in result:
    #             result[doc_key] = {
    #                 'firmname': [], 'firmid': [], 'entityname': [],
    #                 'accountname': [], 'accountsid': [], 'accountuid': [],
    #                 'investor': [], 'is_core_account': False
    #             }
    #         r = result[doc_key]
    #         if row.firm_name: r['firmname'].append(row.firm_name)
    #         if row.firm_id: r['firmid'].append(str(row.firm_id))
    #         if row.entity_name: r['entityname'].append(row.entity_name)
    #         if visibility == 'S':
    #             if row.tokenized_account_name: r['accountname'].append(row.tokenized_account_name)
    #             if row.tokenized_investor: r['investor'].append(row.tokenized_investor)
    #         else:
    #             if row.account_name: r['accountname'].append(row.account_name)
    #             if row.investor: r['investor'].append(row.investor)
    #         if row.account_sid: r['accountsid'].append(row.account_sid)
    #         if row.account_uid: r['accountuid'].append(str(row.account_uid))
    #         if row.firm_system == 'Core': r['is_core_account'] = True
    #     for doc_key in result:
    #         for field in ['firmname', 'firmid', 'entityname', 'accountname', 'accountsid', 'accountuid', 'investor']:
    #             values = list(set(result[doc_key][field]))
    #             result[doc_key][field] = ', '.join(values) if values else None
    #     return result
    
    # def _get_business_dates(self, doc_uids: List[UUID]) -> Dict[str, str]:
    #     """Get aggregated business dates."""
    #     from sqlalchemy import literal
    #     query = self.db.query(
    #         ExtractFile.fileuid,
    #         func.string_agg(
    #             cast(ExtractFile.businessdate, String), 
    #             literal(', ', type_=String(5))
    #         ).label('dates')
    #     ).filter(
    #         ExtractFile.fileuid.in_(doc_uids),
    #         ExtractFile.isactive == True
    #     ).group_by(ExtractFile.fileuid).all()
    #     return {str(row.fileuid): row.dates for row in query}
    
    # def _get_ingestion_counts(self, doc_uids: List[UUID]) -> Dict[str, Dict]:
    #     """Get ingestion status counts."""
    #     query = self.db.query(
    #         ExtractFile.fileuid, ExtractFile.ingestionstatus,
    #         ExtractFile.ismanualingested, func.count().label('cnt')
    #     ).filter(
    #         ExtractFile.fileuid.in_(doc_uids), ExtractFile.isactive == True
    #     ).group_by(
    #         ExtractFile.fileuid, ExtractFile.ingestionstatus, ExtractFile.ismanualingested
    #     ).all()
    #     result = {}
    #     for row in query:
    #         doc_key = str(row.fileuid)
    #         if doc_key not in result:
    #             result[doc_key] = {'in_progress': 0, 'failed': 0, 'manual': 0, 'done': 0, 'total': 0}
    #         status = (row.ingestionstatus or '').lower().strip()
    #         r = result[doc_key]
    #         if status in ['in progress', 'inprogress', '']: r['in_progress'] += row.cnt
    #         elif status == 'failed': r['failed'] += row.cnt
    #         elif status == 'success':
    #             if row.ismanualingested: r['manual'] += row.cnt
    #             else: r['done'] += row.cnt
    #         r['total'] = r['in_progress'] + r['failed'] + r['manual'] + r['done']
    #     return result
