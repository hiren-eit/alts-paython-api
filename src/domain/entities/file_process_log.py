import uuid
from sqlalchemy import Column, String, Text, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from src.domain.entities.base_entity import BaseEntity
from src.domain.enums.file_porcess_log_enums import FileProcessStatus, FileProcessStage
from src.domain.enums.sql_enum import SqlEnum


class FileProcessLog(BaseEntity):
    __tablename__ = "tbl_file_process_log"
    __table_args__ = {"schema": "frame"}

    fileprocesslogid = Column(BigInteger, primary_key=True, autoincrement=True)

    fileuid = Column(UUID(as_uuid=True), nullable=False, index=True)
    status = Column(SqlEnum(FileProcessStatus, name="fileprocessstatus"), nullable=True)
    stage = Column(SqlEnum(FileProcessStage, name="fileprocessstage"), nullable=True)
    filetype = Column(String(50))
    fileprocessstage = Column("fileprocessstage", String(255), nullable=True)
    ruleid = Column(String(450), nullable=True)
    remark = Column(String(500), nullable=True)
    statuscomment = Column(String(500), nullable=True)

    # isactive, created, createdby, updated, updatedby are inherited from BaseEntity
