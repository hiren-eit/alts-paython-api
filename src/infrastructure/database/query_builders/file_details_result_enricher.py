from typing import Optional, Dict, Tuple
from datetime import datetime
from sqlalchemy.orm import Session

from src.domain.dtos.file_details_dto import FileDetailsItem
from src.domain.entities.file_manager import FileManager
from src.domain.entities.file_configuration import FileConfiguration


class FileDetailsResultEnricher:
    """
    Enriches the FileManager entity into a comprehensive FileDetailsItem DTO.
    This class handles logic for calculating derived fields such as Age and SLA Status.
    """

    def __init__(self, db: Session):
        self.db = db

    def enrich(self, file: FileManager) -> Optional[Dict]:
        """
        Transform a FileManager entity into a dictionary representation of FileDetailsItem.

        Args:
            file (FileManager): The file entity to enrich.

        Returns:
            Optional[Dict]: The enriched file details as a dictionary, or None if input is invalid.
        """
        if not file:
            return None

        # 1. Compute File Age
        age = self._calculate_age(file)

        # 2. Calculate SLA Details
        sla_days = self._get_sla_threshold_days(file)
        age_sla_display, sla_status = self._determine_sla_status(age, sla_days)

        # 3. Construct DTO
        details_item = FileDetailsItem(
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
            filetypeprocessrule=file.filetypeprocessrule,
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
        )

        return details_item.model_dump()

    def _calculate_age(self, file: FileManager) -> int:
        """
        Calculate the age of the file in days.
        """
        age = file.age or 0
        if file.createdate:
            # Calculate difference from current UTC time
            delta = datetime.utcnow() - file.createdate.replace(tzinfo=None)
            age = delta.days
        return age

    def _get_sla_threshold_days(self, file: FileManager) -> int:
        """
        Determine the SLA day threshold based on file status and type.
        """
        # Select configuration name based on status
        completed_statuses = {"Linked", "Approved", "Ingested", "Completed", "Ignored"}
        config_name = (
            file.filetypegenai
            if file.status in completed_statuses
            else file.filetypeproceesrule
        )

        if not config_name:
            return 0

        config = (
            self.db.query(FileConfiguration.sla_days)
            .filter(
                FileConfiguration.configurationname == config_name,
                FileConfiguration.isactive == True,
            )
            .first()
        )

        return config.sla_days if config else 0

    def _determine_sla_status(
        self, age: int, sla_days: Optional[int]
    ) -> Tuple[str, Optional[str]]:
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
