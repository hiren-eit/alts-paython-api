from uuid import uuid4
from sqlalchemy import (
    UUID, BigInteger, Column, DateTime, Boolean, Integer, Text, String
)

from src.domain.entities.base_entity import BaseEntity

class FileConfigurationLog(BaseEntity):

    __tablename__ = "tbl_fileconfigurationlog"
    __table_args__ = {'schema': 'frame'}

    fileid = Column(BigInteger, primary_key=True, autoincrement=True)
    fileconfigurationid = Column(BigInteger, nullable=True)
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)