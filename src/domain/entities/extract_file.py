import uuid
from sqlalchemy import (
    UUID, BigInteger, Column, TIMESTAMP, DateTime, Boolean, Integer, Text, String, Date
)
from src.domain.entities.base_entity import BaseEntity

class ExtractFile(BaseEntity):
    __tablename__ = "tbl_extractfile"
    __table_args__ = {'schema': 'frame'}

    recid = Column(BigInteger, primary_key=True, autoincrement=True)
    fileuid = Column(UUID(as_uuid=True), nullable=False, default=uuid.uuid4)
    fileconfigurationid = Column(UUID(as_uuid=True), nullable=True)
    filetype = Column(Text, nullable=True)
    extracteddata = Column(Text, nullable=True)
    investor = Column(Text, nullable=True)
    account = Column(Text, nullable=True)
    account_uid = Column(UUID(as_uuid=True), nullable=True)
    account_sid = Column(Text, nullable=True)
    firm_id = Column(Integer, nullable=True)
    entity_uid = Column(UUID(as_uuid=True), nullable=True)
    token = Column(Text, nullable=True)
    ingestiontoken = Column(Text, nullable=True)
    businessdate = Column(Date, nullable=True)
    # isactive, created, createdby, updated, updatedby are inherited from BaseEntity
    islinked = Column(Boolean, nullable=False, default=False)
    isignored = Column(Boolean, nullable=False, default=False)
    ignorecomment = Column(Text, nullable=True)
    batchid = Column(Text, nullable=True)
    ingestionstatus = Column(String(10), nullable=True)
    ingestionlog = Column(Text, nullable=True)
    ismanualingested = Column(Boolean, default=False)
    ingestedby = Column(String(100), nullable=True)
