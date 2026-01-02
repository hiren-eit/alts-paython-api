"""
File Manager Result Enricher
Handles post-query mapping from entity to DTO.
"""

from datetime import datetime
from typing import List, Dict
from uuid import UUID
from sqlalchemy.orm import Session

from src.domain.dtos.file_manager_dto import FileManagerFilter, FileManagerItem
from src.domain.entities.file_manager import FileManager
from src.domain.entities.file_configuration import FileConfiguration
from src.domain.entities.extract_file import ExtractFile
from src.domain.entities.account_master import AccountMaster
from src.domain.entities.firm_master import FirmMaster
from src.domain.entities.publishing_control import PublishingControl
from sqlalchemy import func, cast, String

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

        # Batch fetch extra data
        file_uids = [f.fileuid for f in results]
        account_info = self._get_account_info(file_uids)
        business_dates = self._get_business_dates(file_uids)
        ingestion_counts = self._get_ingestion_counts(file_uids)
        pub_uids = self._get_pub_uids(file_uids)

        # Build enriched items
        items = []
        for file in results:
            uid_str = str(file.fileuid)
            item = self._build_item(
                file, 
                account_info.get(uid_str, {}),
                business_dates.get(uid_str),
                ingestion_counts.get(uid_str, {}),
                pub_uids.get(uid_str)
            )
            items.append(item)

        return items

    def _build_item(self, file: FileManager, account: Dict, business_date: str, counts: Dict, pub_uid: str) -> Dict:
        """Build a single item mapping entity to DTO with SLA info."""
        # Get SLA info
        config_name = (
            file.filetypegenai
            if file.status in ["Linked", "Approved", "Ingested", "Completed", "Ignored"]
            else file.filetypeprocessrule
        )
        sla_days = self._config_map.get(config_name, 0)

        # Calculate age
        if file.status == "Ingested" and file.age is not None:
            age = file.age
        elif file.createdate:
            age = (datetime.utcnow() - file.createdate.replace(tzinfo=None)).days
        else:
            age = file.age or 0

        # Calculate SLA status
        age_sla_display, sla_status = self._calculate_sla_status(age, sla_days)
        tsla_status = self._calculate_tsla_status(age)

        item = FileManagerItem(
            fileid=file.fileid,
            fileuid=file.fileuid,
            type=file.type,
            filename=file.filename,
            firm=account.get('first_firm_id') or file.firm,
            entityuid=account.get('first_entity_uid') or file.entityuid,
            accountsid=account.get('accountsid') or file.accountsid,
            accountuid=account.get('accountuid') or file.accountuid,
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
            filetypeprocessrule=file.filetypeprocessrule,
            filetypegenai=file.filetypegenai,
            ignoredon=file.ignoredon,
            ignoredby=str(file.ignoredby) if file.ignoredby is not None else None,
            rule=file.rule,
            businessdate=business_date or (str(file.businessdate.date()) if file.businessdate else None),
            firmname=account.get('firmname') or file.firmname,
            entityname=account.get('entityname') or file.entityname,
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
            tsla_status=tsla_status,
            sladays=sla_days,
            investor=account.get('investor'),
            accountname=account.get('accountname'),
            entityuids=account.get('entityuids'),
            pubuid=pub_uid,
            firmid=account.get('firmid'),
            iscoreaccount=account.get('is_core_account', False),
            totalingestioncount=str(counts.get('total', 0)),
            ingestioninprogresscount=counts.get('in_progress', 0),
            ingestionfailedcount=counts.get('failed', 0),
            manualingestedcount=counts.get('manual', 0),
            ingestiondonecount=counts.get('done', 0)
        )
        return item.model_dump(by_alias=True)

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
        configs = (
            self.db.query(
                FileConfiguration.configurationname, FileConfiguration.sla_days
            )
            .filter(
                FileConfiguration.isactive == True,
                FileConfiguration.sla_days.isnot(None),
            )
            .all()
        )
        return {c.configurationname: c.sla_days for c in configs}

    # =========================================================================
    # ARCHIVED METHODS (Commented out for future use)
    # =========================================================================

    def _get_account_info(self, file_uids: List[UUID]) -> Dict[str, Dict]:
        """Get account information with aggregation."""
        results = self.db.query(
            ExtractFile.fileuid,
            ExtractFile.investor.label('ef_investor'),
            ExtractFile.account.label('ef_account_name'),
            ExtractFile.account_sid.label('ef_account_sid'),
            ExtractFile.account_uid.label('ef_account_uid'),
            ExtractFile.entity_uid.label('ef_entity_uid'),
            ExtractFile.firm_id.label('ef_firm_id'),
            AccountMaster.firm_name,
            AccountMaster.firm_id,
            AccountMaster.entity_name,
            AccountMaster.account_name,
            AccountMaster.tokenized_account_name,
            AccountMaster.accounts_id.label('account_sid'),
            AccountMaster.account_uid,
            AccountMaster.entity_uid,
            AccountMaster.investor,
            AccountMaster.tokenized_investor,
            FirmMaster.system.label('firm_system')
        ).outerjoin(
            AccountMaster, 
            (ExtractFile.account_uid == AccountMaster.account_uid) & 
            (AccountMaster.isactive == True)
        ).outerjoin(
            FirmMaster, (ExtractFile.firm_id == FirmMaster.firm_id) & (FirmMaster.isactive == True)
        ).filter(
            ExtractFile.fileuid.in_(file_uids),
            ExtractFile.isactive == True,
            ExtractFile.islinked == True
        ).all()

        for r in results:
            pass  # Query executed, results ready for aggregation
        
        return self._aggregate_account_info(results)

    def _aggregate_account_info(self, query_results) -> Dict[str, Dict]:
        """Aggregate account info by file_uid."""
        result = {}
        visibility = self.filters.visibility
        for row in query_results:
            file_key = str(row.fileuid)
            if file_key not in result:
                result[file_key] = {
                    'firmname': [], 'firmid': [], 'entityname': [],
                    'accountname': [], 'accountsid': [], 'accountuid': [],
                    'entityuids': [],
                    'investor': [], 'is_core_account': False,
                    'first_firm_id': None, 'first_entity_uid': None
                }
            r = result[file_key]
            
            # Use AccountMaster data if available, fallback to ExtractFile data
            firm_name = row.firm_name
            firm_id = row.firm_id or row.ef_firm_id
            entity_name = row.entity_name
            
            if visibility == 'S':
                # Tokenized mode: Only use tokenized fields from AccountMaster
                account_name = row.tokenized_account_name
                investor = row.tokenized_investor
            else:
                # Normal mode: Use AccountMaster or fallback to ExtractFile
                account_name = row.account_name or row.ef_account_name
                investor = row.investor or row.ef_investor
                
            account_sid = row.account_sid or row.ef_account_sid
            account_uid = row.account_uid or row.ef_account_uid
            entity_uid = row.entity_uid or row.ef_entity_uid

            if firm_name: r['firmname'].append(firm_name)
            if firm_id: r['firmid'].append(str(firm_id))
            if entity_name: r['entityname'].append(entity_name)
            if account_name: r['accountname'].append(account_name)
            if investor: r['investor'].append(investor)
            if account_sid: r['accountsid'].append(account_sid)
            if account_uid: r['accountuid'].append(str(account_uid))
            if entity_uid: r['entityuids'].append(str(entity_uid))
            
            if r['first_firm_id'] is None: r['first_firm_id'] = firm_id
            if r['first_entity_uid'] is None: r['first_entity_uid'] = entity_uid
            if row.firm_system == 'Core': r['is_core_account'] = True
            
        for file_key in result:
            for field in ['firmname', 'firmid', 'entityname', 'accountname', 'accountsid', 'accountuid', 'investor', 'entityuids']:
                values = list(set([v for v in result[file_key][field] if v]))
                result[file_key][field] = ', '.join(values) if values else None
        return result

    def _get_business_dates(self, file_uids: List[UUID]) -> Dict[str, str]:
        """Get aggregated business dates."""
        query = self.db.query(
            ExtractFile.fileuid,
            func.string_agg(
                cast(ExtractFile.businessdate, String),
                ', '
            ).label('dates')
        ).filter(
            ExtractFile.fileuid.in_(file_uids),
            ExtractFile.isactive == True
        ).group_by(ExtractFile.fileuid).all()
        return {str(row.fileuid): row.dates for row in query}

    def _get_ingestion_counts(self, file_uids: List[UUID]) -> Dict[str, Dict]:
        """Get ingestion status counts."""
        query = self.db.query(
            ExtractFile.fileuid, ExtractFile.ingestionstatus,
            ExtractFile.ismanualingested, func.count().label('cnt')
        ).filter(
            ExtractFile.fileuid.in_(file_uids), ExtractFile.isactive == True
        ).group_by(
            ExtractFile.fileuid, ExtractFile.ingestionstatus, ExtractFile.ismanualingested
        ).all()
        result = {}
        for row in query:
            file_key = str(row.fileuid)
            if file_key not in result:
                result[file_key] = {'in_progress': 0, 'failed': 0, 'manual': 0, 'done': 0, 'total': 0}
            status = (row.ingestionstatus or '').lower().strip()
            r = result[file_key]
            if status in ['in progress', 'inprogress', '']: r['in_progress'] += row.cnt
            elif status == 'failed': r['failed'] += row.cnt
            elif status == 'success':
                if row.ismanualingested: r['manual'] += row.cnt
                else: r['done'] += row.cnt
            r['total'] = r['in_progress'] + r['failed'] + r['manual'] + r['done']
        return result

    def _get_pub_uids(self, file_uids: List[UUID]) -> Dict[str, str]:
        """Get aggregated publishing control IDs."""
        query = self.db.query(
            ExtractFile.fileuid,
            func.string_agg(
                cast(PublishingControl.pub_id, String),
                ', '
            ).label('pub_ids')
        ).join(
            PublishingControl, 
            (ExtractFile.account_uid == PublishingControl.account_uid) & 
            (ExtractFile.businessdate == PublishingControl.business_date)
        ).filter(
            ExtractFile.fileuid.in_(file_uids),
            ExtractFile.isactive == True,
            ExtractFile.islinked == True,
            PublishingControl.isactive == True
        ).group_by(ExtractFile.fileuid).all()
        return {str(row.fileuid): row.pub_ids for row in query}
