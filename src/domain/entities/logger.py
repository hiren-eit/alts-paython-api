from sqlalchemy import Column, Text, BigInteger
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP

from .base_entity import BaseEntity

class Logs(BaseEntity):
    __tablename__ = "tbl_logs"
    __table_args__ = {'schema': 'frame'}

    logid = Column(BigInteger, primary_key=True, autoincrement=True)
    message = Column(Text, nullable=True)
    message_template = Column(Text, nullable=True)
    level = Column(Text, nullable=True)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=True)
    exception = Column(Text, nullable=True)
    log_event = Column(JSONB, nullable=True)
