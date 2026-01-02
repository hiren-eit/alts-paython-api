from sqlalchemy import (
    UUID,
    BigInteger,
    Column,
    DateTime,
    Boolean,
    Integer,
    Text,
    String,
)

from src.domain.entities.base_entity import BaseEntity


class FileConfiguration(BaseEntity):
    __tablename__ = "tbl_file_configuration"
    __table_args__ = {"schema": "frame"}

    fileid = Column(BigInteger, primary_key=True, autoincrement=True)
    configurationname = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    sla_priority = Column(Integer, nullable=True)
    sla_days = Column(Integer, nullable=True)
    schematype = Column(String(50), nullable=False)
    extraction = Column(String(100), nullable=True)
    reason = Column(Text, nullable=True)
    filetypeid = Column(UUID(as_uuid=True), nullable=True)
    ingestioncode = Column(Integer, nullable=True)
    fieldtype = Column(Text, nullable=True)
