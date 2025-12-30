from sqlalchemy import (
    UUID, Column, DateTime, Boolean, Integer, Text, BigInteger
)

from src.domain.entities.base_entity import BaseEntity

class AccountMaster(BaseEntity):
    __tablename__ = "tbl_account_master"
    __table_args__ = {'schema': 'frame'}

    accountmasterid = Column(BigInteger, primary_key=True, autoincrement=True)
    account_uid = Column(UUID(as_uuid=True), nullable=True)
    accounts_id = Column(Text, nullable=True)
    entity_uid = Column(UUID(as_uuid=True), nullable=True)
    firm_id = Column(Integer, nullable=True)
    created = Column(DateTime, nullable=True)
    frequency = Column(Text, nullable=True)
    delay = Column(Integer, nullable=True)
    annual_delay = Column(Integer, nullable=True)
    firm_name = Column(Text, nullable=True)
    entity_name = Column(Text, nullable=True)
    account_name = Column(Text, nullable=True)
    investor = Column(Text, nullable=True)
    tokenized_account_name = Column(Text, nullable=True)
    tokenized_investor = Column(Text, nullable=True)
    reason_for_toggle = Column(Text, nullable=True)
    create_date = Column(DateTime, nullable=True)
    account_status = Column(Text, nullable=True)
    account_status_date = Column(DateTime, nullable=True)
    source_uid = Column(UUID(as_uuid=True), nullable=True)
    institution_name = Column(Text, nullable=True)
    manager_type = Column(Text, nullable=True)
