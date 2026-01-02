import uuid
from sqlalchemy import Column, String, Text, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from src.domain.entities.base_entity import BaseEntity

class FileProcessLog(BaseEntity):
    __tablename__ = "tbl_file_process_log"
    __table_args__ = {'schema': 'frame'}

    fileprocesslogid = Column(BigInteger, primary_key=True, autoincrement=True)
    fileuid = Column(UUID(as_uuid=True))  # Maps to FileUID
    stage = Column(String(100))
    status = Column(String(100))
    ruleid = Column(String(255), nullable=True)
    statuscomment = Column(Text)
    fileprocessstage = Column(String(100)) # Maps to fileProcessStage log

    # isactive, created, createdby, updated, updatedby are inherited from BaseEntity
