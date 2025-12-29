from sqlalchemy import (
    UUID, Column, DateTime, Boolean, Integer, Text, String, Date, BigInteger
)

from src.domain.entities.base_entity import BaseEntity

class PublishingControl(BaseEntity):
    __tablename__ = "tbl_publishing_control"
    __table_args__ = {'schema': 'frame'}

    publishingcontrolid = Column(BigInteger, primary_key=True, autoincrement=True)
    
    account_uid = Column(UUID(as_uuid=True), nullable=True)
    business_date = Column(Date, nullable=True)
    expected_date = Column(Date, nullable=True)
    received_date = Column(Date, nullable=True)
    file_type = Column(Text, nullable=True)
    pub_status = Column(Text, nullable=True)
    delay = Column(Integer, nullable=True)
    annual_delay = Column(Integer, nullable=True)
    pub_id = Column(UUID(as_uuid=True), nullable=True)
    frequency = Column(Text, nullable=True)
    change_type = Column(String(10), nullable=True)
