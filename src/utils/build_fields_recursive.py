from uuid import uuid4
from sqlalchemy import UUID
from src.domain.enums import DataTypes
from src.domain.entities.file_configuration_field import FileConfigurationField


def build_fields_recursive(
    field_schema: FileConfigurationField,
    document_id: int | None,
    parent_id: int | None,
    collected: list
):
    field = FileConfigurationField(
        fieldname=field_schema.fieldname,
        datatype=field_schema.datatype,
        description=field_schema.description,
        mandatory=field_schema.mandatory,
        isactive=field_schema.isactive,
        fileconfigurationid=document_id,
        parentfieldid=parent_id,
    )

    collected.append(field)

    if field_schema.datatype in (DataTypes.ARRAY, DataTypes.OBJECT):
        for sub in field_schema.subRows or []:
            build_fields_recursive(sub, document_id, field.fileid, collected)
