import datetime
from time import timezone
from uuid import UUID, uuid4
from typing import List, Tuple
import json
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from src.domain.dtos.document_configuration_dto import DocumentConfiguration
from src.domain.entities.file_configuration import FileConfiguration
from src.domain.entities.file_configuration_field import FileConfigurationField
from src.domain.entities.file_configuration_log import FileConfigurationLog
from src.domain.enums import DataTypes
from src.utils.build_fields_recursive import build_fields_recursive
from datetime import datetime, timezone

class UpdateDocumentConfiguration:
    """
    Handles database operations for UpdateDocumentConfiguration
    """

    def __init__(self, db: Session):
        self.db = db

    def get_document_configuration(self, config_id: int) -> FileConfiguration:
        """
        Fetches the existing document configuration from the database.
        """
        stmt = select(FileConfiguration).where(FileConfiguration.fileid == config_id)
        return self.db.execute(stmt).scalar_one_or_none()


    def update_configuration(self, configuration: FileConfiguration, updated_by: str) -> None:
        """
        Updates the FileConfiguration in the database.
        """
        stmt = update(FileConfiguration).where(FileConfiguration.fileid == configuration.fileid).values(
            # configurationname=configuration.configurationname,
            # description=configuration.description,
            # sla_priority=configuration.sla_priority,
            # sla_days=configuration.sla_days,
            # schematype=configuration.schematype,
            # extraction=configuration.extraction,
            # filetypeid=configuration.filetypeid,
            # reason=configuration.reason,
            # fieldtype=configuration.fieldtype,
            # ingestioncode=configuration.ingestioncode,
            # isactive=configuration.isactive,
            updated=datetime.utcnow(),
            updatedby=len(updated_by),
        )
        self.db.execute(stmt)
        self.db.commit()

    def save_log(self, configuration_id: int, changes: str, created_by: int) -> None:
        """
        Save the configuration change log.
        """
        log_entry = FileConfigurationLog(
            fileconfigurationid=configuration_id,
            title="Configuration Modified",
            description=changes,
            createdby=created_by,
            created=datetime.utcnow(),
            isactive=True
        )
        self.db.add(log_entry)
        self.db.commit()

    def commit(self):
        """
        Commit the transaction.
        """
        self.db.commit()

    def rollback(self):
        """
        Rollback the transaction in case of an error.
        """
        self.db.rollback()