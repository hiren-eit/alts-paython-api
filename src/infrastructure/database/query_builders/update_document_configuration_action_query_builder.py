import datetime
from time import timezone
from uuid import UUID, uuid4
from typing import List, Tuple
import json
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from src.domain.dtos.document_configuration_dto import DocumentConfigurationLog
from src.domain.entities.file_configuration import FileConfiguration
from src.domain.entities.file_configuration_field import FileConfigurationField
from src.domain.entities.file_configuration_log import FileConfigurationLog
from src.domain.enums import DataTypes
from src.utils.build_fields_recursive import build_fields_recursive
from datetime import datetime, timezone

class UpdateDocumentConfigurationActionQueryBuilder:
    """
    Handles database operations for UpdateDocumentConfigurationAction
    """
    def __init__(self, db: Session):
        self.db = db
    
    def configuration_exists(self, configuration_name: str) -> bool:
        stmt = select(FileConfiguration).where(FileConfiguration.configurationname == configuration_name)
        return self.db.execute(stmt).scalar_one_or_none() is not None

    def save_log(self, log_entry: FileConfigurationLog) -> bool:
        try:
            self.db.add(log_entry)
            self.db.commit()
            return True
        except Exception as ex:
            return False

    def get_document_configuration(self, id: int) -> FileConfiguration:
        # Fetch the document configuration from the database by its ID
        return self.db.query(FileConfiguration).filter(FileConfiguration.fileid == id).first()

    def update_document_configuration_in_db(self):
        try:
            self.db.commit()
        except Exception as ex:
            self.db.rollback()