import uuid
from sqlalchemy import (
    UUID, BigInteger, Column, TIMESTAMP, Boolean, Integer, Text, String, Date
)
from src.domain.entities.base_entity import BaseEntity

class ExtractionFileDetail(BaseEntity):
    __tablename__ = "tbl_extractionfiledetail"
    __table_args__ = {'schema': 'frame'}

    recid = Column(BigInteger, primary_key=True, autoincrement=True)
    fileuid = Column(UUID(as_uuid=True), nullable=False, default=uuid.uuid4)
    classification = Column(Text)
    extraction_data = Column(Text)
    bounding_box_data = Column(Text)
    confidence_scores = Column(Text)
    duplicate_flag = Column(Boolean)
    duplicate_file_id = Column(UUID(as_uuid=True))
    update_flag = Column(Boolean)
    update_file_id = Column(UUID(as_uuid=True))
    message = Column(Text)
    timestamp = Column(Text)
    status = Column(Boolean, nullable=False)
    # isactive, created, createdby, updated, updatedby are inherited from BaseEntity
    isupdate = Column(Boolean, default=False)
    type = Column(Text)
    ismanual = Column(Boolean, nullable=False, default=False)
    isadd = Column(Boolean, nullable=False, default=False)
