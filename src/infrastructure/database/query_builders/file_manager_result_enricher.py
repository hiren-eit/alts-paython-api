"""
File Manager Result Enricher
Handles post-query mapping from entity to DTO.
"""
from datetime import datetime
from typing import List, Dict
from sqlalchemy.orm import Session

from src.domain.dtos.file_manager_dto import FileManagerFilter, FileManagerItem
from src.domain.entities.file_manager import FileManager
from src.domain.entities.file_configuration import FileConfiguration


class FileManagerResultEnricher:
    """
    Enriches query results by mapping FileManager entity to FileManagerItem DTO.
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
        for file in results:
            item = self._build_item(file)
            items.append(item)
        
        return items
    
    def _build_item(self, file: FileManager) -> Dict:
        """Build a single item mapping entity to DTO with SLA info."""
        # Get SLA info
        config_name = (
            file.filetypegenai 
            if file.status in ['Linked', 'Approved', 'Ingested', 'Completed', 'Ignored']
            else file.filetypeproceesrule
        )
        sla_days = self._config_map.get(config_name, 0)

        # Calculate age
        age = file.age or 0
        if file.createdate:
            age = (datetime.utcnow() - file.createdate.replace(tzinfo=None)).days
        
        # Calculate SLA status
        age_sla_display, sla_status = self._calculate_sla_status(age, sla_days)
        tsla_status = self._calculate_tsla_status(age)

        item = FileManagerItem(
            fileid=file.fileid,
            fileuid=file.fileuid,
            type=file.type,
            filename=file.filename,
            firm=file.firm,
            entityuid=file.entityuid,
            accountsid=file.accountsid,
            accountuid=file.accountuid,
            filepath=file.filepath,
            createdate=file.createdate,
            createtime=file.createtime,
            comments=file.comments,
            createby=str(file.createby) if file.createby is not None else None,
            filenameframe=file.filenameframe,
            batchid=file.batchid,
            metadata=file.file_metadata,
            checksum=file.checksum,
            status=file.status,
            statusdate=file.statusdate,
            method=file.method,
            reasonid=file.reasonid,
            reason=file.reason,
            harvestsystem=file.harvestsystem,
            harvestmethod=file.harvestmethod,
            harvestsource=file.harvestsource,
            indexsystem=file.indexsystem,
            indexmethod=file.indexmethod,
            extractsystem=file.extractsystem,
            extractmethod=file.extractmethod,
            age=age,
            emailsender=file.emailsender,
            emailsubject=file.emailsubject,
            category=file.category,
            failurestage=file.failurestage,
            filetypeproceesrule=file.filetypeproceesrule,
            filetypegenai=file.filetypegenai,
            ignoredon=file.ignoredon,
            ignoredby=str(file.ignoredby) if file.ignoredby is not None else None,
            rule=file.rule,
            businessdate=str(file.businessdate.date()) if file.businessdate else None,
            firmname=file.firmname,
            entityname=file.entityname,
            capturemethod=file.capturemethod,
            linkingmethod=file.linkingmethod,
            stage=file.stage,
            isactive=file.isactive,
            updatefileid=file.updatefileid,
            statuscomment=file.statuscomment,
            duplicatefileid=file.duplicatefileid,
            fileprocessstage=file.fileprocessstage,
            businessruleapplieddate=file.businessruleapplieddate,
            fileextension=file.fileextension,
            password=file.password,
            groupcode=file.groupcode,
            replay=file.replay,
            lastattemptedtime=file.lastattemptedtime,
            retrycount=file.retrycount,
            ingestionfailedimageurl=file.ingestionfailedimageurl,
            created=file.created,
            createdby=str(file.createdby) if file.createdby is not None else None,
            updated=file.updated,
            updatedby=str(file.updatedby) if file.updatedby is not None else None,
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
    
    # def _get_account_info(self, file_uids: List[UUID]) -> Dict[str, Dict]:
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
    #         ExtractFile.fileuid.in_(file_uids),
    #         ExtractFile.isactive == True,
    #         ExtractFile.islinked == True,
    #         AccountMaster.isactive == True
    #     ).all()
    #     return self._aggregate_account_info(query)
    
    # def _aggregate_account_info(self, query_results) -> Dict[str, Dict]:
    #     """Aggregate account info by file_uid."""
    #     result = {}
    #     visibility = self.filters.visibility
    #     for row in query_results:
    #         file_key = str(row.fileuid)
    #         if file_key not in result:
    #             result[file_key] = {
    #                 'firmname': [], 'firmid': [], 'entityname': [],
    #                 'accountname': [], 'accountsid': [], 'accountuid': [],
    #                 'investor': [], 'is_core_account': False
    #             }
    #         r = result[file_key]
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
    #     for file_key in result:
    #         for field in ['firmname', 'firmid', 'entityname', 'accountname', 'accountsid', 'accountuid', 'investor']:
    #             values = list(set(result[file_key][field]))
    #             result[file_key][field] = ', '.join(values) if values else None
    #     return result
    
    # def _get_business_dates(self, file_uids: List[UUID]) -> Dict[str, str]:
    #     """Get aggregated business dates."""
    #     from sqlalchemy import literal
    #     query = self.db.query(
    #         ExtractFile.fileuid,
    #         func.string_agg(
    #             cast(ExtractFile.businessdate, String), 
    #             literal(', ', type_=String(5))
    #         ).label('dates')
    #     ).filter(
    #         ExtractFile.fileuid.in_(file_uids),
    #         ExtractFile.isactive == True
    #     ).group_by(ExtractFile.fileuid).all()
    #     return {str(row.fileuid): row.dates for row in query}
    
    # def _get_ingestion_counts(self, file_uids: List[UUID]) -> Dict[str, Dict]:
    #     """Get ingestion status counts."""
    #     query = self.db.query(
    #         ExtractFile.fileuid, ExtractFile.ingestionstatus,
    #         ExtractFile.ismanualingested, func.count().label('cnt')
    #     ).filter(
    #         ExtractFile.fileuid.in_(file_uids), ExtractFile.isactive == True
    #     ).group_by(
    #         ExtractFile.fileuid, ExtractFile.ingestionstatus, ExtractFile.ismanualingested
    #     ).all()
    #     result = {}
    #     for row in query:
    #         file_key = str(row.fileuid)
    #         if file_key not in result:
    #             result[file_key] = {'in_progress': 0, 'failed': 0, 'manual': 0, 'done': 0, 'total': 0}
    #         status = (row.ingestionstatus or '').lower().strip()
    #         r = result[file_key]
    #         if status in ['in progress', 'inprogress', '']: r['in_progress'] += row.cnt
    #         elif status == 'failed': r['failed'] += row.cnt
    #         elif status == 'success':
    #             if row.ismanualingested: r['manual'] += row.cnt
    #             else: r['done'] += row.cnt
    #         r['total'] = r['in_progress'] + r['failed'] + r['manual'] + r['done']
    #     return result
