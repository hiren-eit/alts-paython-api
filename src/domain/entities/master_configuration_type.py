import uuid
from sqlalchemy import Column, String, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from src.domain.entities.base_entity import BaseEntity


class MasterConfigurationType(BaseEntity):
    __tablename__ = "tbl_master_configuration_type"
    __table_args__ = {"schema": "frame"}

    masterconfigurationtypeid = Column(
        BigInteger, primary_key=True, autoincrement=True, name="id"
    )
    displayname = Column(String(255))
    type = Column(String(255))
    code = Column(String(255))
    # isactive, created, createdby, updated, updatedby are inherited from BaseEntity
