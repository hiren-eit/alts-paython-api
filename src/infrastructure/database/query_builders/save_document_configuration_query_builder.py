import datetime
from time import timezone
from uuid import UUID, uuid4
from typing import List, Tuple
import json
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.domain.dtos.file_configuration_dto import FileConfiguration as FileFileConfigurationDTO
from src.domain.entities.file_configuration import FileConfiguration
from src.domain.entities.file_configuration_field import FileConfigurationField
from src.domain.entities.file_configuration_log import FileConfigurationLog
from datetime import datetime, timezone

class SaveDocumentConfigurationQueryBuilder:
    """
    Handles ALL database operations for SaveDocumentConfiguration
    """

    def __init__(self, db: Session):
        self.db = db

    def configuration_exists(self, configuration_name: str) -> bool:
        stmt = select(FileConfiguration).where(
            FileConfiguration.configurationname == configuration_name
        )
        return self.db.execute(stmt).scalar_one_or_none() is not None

    def create_document_with_fields(
        self, document_configuration: FileFileConfigurationDTO
    ) -> Tuple[FileConfiguration, int]:
        """
        Creates FileConfiguration + Fields.
        Returns created configuration and total fields count.
        """
        sub_rows_to_add: List[FileConfigurationField] = []

        configuration = FileConfiguration(
            configurationname=document_configuration.configuration_name,
            description=document_configuration.description,
            sla_priority=document_configuration.sla_priority,
            sla_days=document_configuration.sla_days,
            schematype=document_configuration.schema_type,
            extraction=document_configuration.extraction,
            filetypeid=document_configuration.document_type_id,
            reason=document_configuration.reason,
            fieldtype=document_configuration.field_type,
            ingestioncode=document_configuration.ingestion_code,
            created=document_configuration.created,
            createdby=len(document_configuration.created_by),
            isactive=document_configuration.is_active,
        )

        self.db.add(configuration)
        self.db.flush()  # PK available

        for field in document_configuration.fields_collection:
            root_field = FileConfigurationField(
                fieldname=field.field_name,
                datatype=field.data_type,
                description=field.description,
                mandatory=field.mandatory,
                fileconfigurationid=configuration.fileid,
                parentfieldid=None,
                created=configuration.created,
                createdby=configuration.createdby,
                isactive=True,
            )

            sub_rows_to_add.append(root_field)

            if field.data_type in ("Array", "Object"):
                for sub_row in field.sub_rows or []:
                    self._add_sub_rows_recursive(
                        sub_row,
                        configuration.fileid,
                        root_field,
                        sub_rows_to_add,
                    )

        if sub_rows_to_add:
            self.db.add_all(sub_rows_to_add)

        return configuration, len(sub_rows_to_add)

    def save_log(
        self,
        configuration_id: int,
        fields_count: int,
        created_by: int,
    ):
        log_payload = json.dumps(
            [
                {
                    "description": f"{fields_count} Fields Added",
                    "changeType": "Added",
                }
            ]
        )

        log_entry = FileConfigurationLog(
            fileconfigurationid=configuration_id,
            title="New Configuration Created",
            description=log_payload,
            createdby=created_by,
            created=datetime.now(timezone.utc),
            isactive=True,
        )

        self.db.add(log_entry)

    def commit(self):
        self.db.commit()

    def rollback(self):
        self.db.rollback()

    # -----------------------------
    # Internal recursive helper
    # -----------------------------
    def _add_sub_rows_recursive(
        self,
        field_dto,
        file_configuration_id: int,
        parent_field: FileConfigurationField,
        accumulator: List[FileConfigurationField],
    ):
        child = FileConfigurationField(
            fieldname=field_dto.field_name,
            datatype=field_dto.data_type,
            description=field_dto.description,
            mandatory=field_dto.mandatory,
            fileconfigurationid=file_configuration_id,
            parentfieldid=None,  # set after flush
            createdby=len(field_dto.created_by),
            isactive=True,
        )

        self.db.add(child)
        self.db.flush()

        child.parentfieldid = parent_field.fileid
        accumulator.append(child)

        if field_dto.data_type in ("Array", "Object"):
            for sub in field_dto.sub_rows or []:
                self._add_sub_rows_recursive(
                    sub,
                    file_configuration_id,
                    child,
                    accumulator,
                )
