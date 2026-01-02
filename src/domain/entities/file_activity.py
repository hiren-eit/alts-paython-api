import uuid
from sqlalchemy import UUID, BigInteger, Column, Boolean, Text
from src.domain.entities.base_entity import BaseEntity


class FileActivity(BaseEntity):
    __tablename__ = "tbl_fileactivity"
    __table_args__ = {"schema": "frame"}

    fileactivityid = Column(BigInteger, primary_key=True, autoincrement=True)
    fileuid = Column(UUID(as_uuid=True))
    status = Column(Text)
    stage = Column(Text)
    fileprocessingstage = Column(Text)
    failurestage = Column(Text)
    statuscomment = Column(Text)
    comment = Column(Text)
    iscommented = Column(Boolean, default=False)

    __mapper_args__ = {"exclude_properties": ["filedetails"]}

    # isactive, created, createdby, updated, updatedby are inherited from BaseEntity
