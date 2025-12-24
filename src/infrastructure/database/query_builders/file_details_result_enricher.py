from typing import Optional, Dict, Tuple
from datetime import datetime
from sqlalchemy.orm import Session

from src.domain.dtos.file_details_dto import DocumentDetailsItem
from src.domain.entities.file_manager import FileManager
from src.domain.entities.file_configuration import FileConfiguration


class DocumentDetailsResultEnricher:
    """
    Enriches the FileManager entity into a comprehensive DocumentDetailsItem DTO.
    This class handles logic for calculating derived fields such as Age and SLA Status.
    """

    def __init__(self, db: Session):
        self.db = db

    def enrich(self, document: FileManager) -> Optional[Dict]:
        """
        Transform a FileManager entity into a dictionary representation of DocumentDetailsItem.
        
        Args:
            document (FileManager): The document entity to enrich.

        Returns:
            Optional[Dict]: The enriched document details as a dictionary, or None if input is invalid.
        """
        if not document:
            return None

        # 1. Compute Document Age
        age = self._calculate_age(document)

        # 2. Calculate SLA Details
        sla_days = self._get_sla_threshold_days(document)
        age_sla_display, sla_status = self._determine_sla_status(age, sla_days)

        # 3. Construct DTO
        details_item = DocumentDetailsItem(
            fileid=document.fileid,
            fileuid=document.fileuid,
            type=document.type,
            filename=document.filename,
            firm=document.firm,
            entityuid=document.entityuid,
            accountsid=document.accountsid,
            accountuid=document.accountuid,
            filepath=document.filepath,
            createdate=document.createdate,
            createtime=document.createtime,
            comments=document.comments,
            createby=str(document.createby) if document.createby is not None else None,
            filenameframe=document.filenameframe,
            batchid=document.batchid,
            metadata=document.file_metadata,
            checksum=document.checksum,
            status=document.status,
            statusdate=document.statusdate,
            method=document.method,
            reasonid=document.reasonid,
            reason=document.reason,
            harvestsystem=document.harvestsystem,
            harvestmethod=document.harvestmethod,
            harvestsource=document.harvestsource,
            indexsystem=document.indexsystem,
            indexmethod=document.indexmethod,
            extractsystem=document.extractsystem,
            extractmethod=document.extractmethod,
            age=age,
            emailsender=document.emailsender,
            emailsubject=document.emailsubject,
            category=document.category,
            failurestage=document.failurestage,
            filetypeproceesrule=document.filetypeproceesrule,
            filetypegenai=document.filetypegenai,
            ignoredon=document.ignoredon,
            ignoredby=str(document.ignoredby) if document.ignoredby is not None else None,
            rule=document.rule,
            businessdate=str(document.businessdate.date()) if document.businessdate else None,
            firmname=document.firmname,
            entityname=document.entityname,
            capturemethod=document.capturemethod,
            linkingmethod=document.linkingmethod,
            stage=document.stage,
            isactive=document.isactive,
            updatefileid=document.updatefileid,
            statuscomment=document.statuscomment,
            duplicatefileid=document.duplicatefileid,
            fileprocessstage=document.fileprocessstage,
            businessruleapplieddate=document.businessruleapplieddate,
            fileextension=document.fileextension,
            password=document.password,
            groupcode=document.groupcode,
            replay=document.replay,
            lastattemptedtime=document.lastattemptedtime,
            retrycount=document.retrycount,
            ingestionfailedimageurl=document.ingestionfailedimageurl,
            created=document.created,
            createdby=str(document.createdby) if document.createdby is not None else None,
            updated=document.updated,
            updatedby=str(document.updatedby) if document.updatedby is not None else None,
            age_sla_display=age_sla_display,
            sla_status=sla_status
        )

        return details_item.model_dump()

    def _calculate_age(self, document: FileManager) -> int:
        """
        Calculate the age of the document in days.
        """
        age = document.age or 0
        if document.createdate:
            # Calculate difference from current UTC time
            delta = datetime.utcnow() - document.createdate.replace(tzinfo=None)
            age = delta.days
        return age

    def _get_sla_threshold_days(self, document: FileManager) -> int:
        """
        Determine the SLA day threshold based on document status and type.
        """
        # Select configuration name based on status
        completed_statuses = {'Linked', 'Approved', 'Ingested', 'Completed', 'Ignored'}
        config_name = (
            document.filetypegenai 
            if document.status in completed_statuses
            else document.filetypeproceesrule
        )

        if not config_name:
            return 0
            
        config = self.db.query(FileConfiguration.sla_days).filter(
            FileConfiguration.configuration_name == config_name,
            FileConfiguration.isactive == True
        ).first()

        return config.sla_days if config else 0

    def _determine_sla_status(self, age: int, sla_days: Optional[int]) -> Tuple[str, Optional[str]]:
        """
        Calculate the SLA status string and display format.
        
        Returns:
            Tuple[str, Optional[str]]: (age_sla_display, sla_status)
        """
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
