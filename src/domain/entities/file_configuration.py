from sqlalchemy import (
    UUID, BigInteger, Column, DateTime, Boolean, Integer, Text, String
)

from src.domain.entities.base_entity import BaseEntity

class FileConfiguration(BaseEntity):
    __tablename__ = "tbl_file_configuration"
    __table_args__ = {'schema': 'frame'}

    fileconfigurationid = Column(BigInteger, primary_key=True, autoincrement=True)
    configuration_name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    sla_priority = Column(Integer, nullable=True)
    sla_days = Column(Integer, nullable=True)
    schema_type = Column(String(50), nullable=False)
    extraction = Column(String(100), nullable=True)
    reason = Column(Text, nullable=True)
    file_type_id = Column(UUID(as_uuid=True), nullable=True)
    ingestion_code = Column(Integer, nullable=True)
    field_type = Column(Text, nullable=True)
