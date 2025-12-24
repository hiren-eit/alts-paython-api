from sqlalchemy import (
    Column, DateTime, Boolean, Integer, Text, String, BigInteger
)
from src.domain.entities.base_entity import BaseEntity

class FirmMaster(BaseEntity):
    __tablename__ = "firm_master"
    __table_args__ = {'schema': 'frame'}

    firm_id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=True)
    status = Column(Text, nullable=True)
    create_date = Column(DateTime, nullable=True)
    update_date = Column(DateTime, nullable=True)
    firm_parent_id = Column(Integer, nullable=True)
    partner_client_id = Column(Integer, nullable=True)
    system = Column(String(50), nullable=True)
    short_name = Column(String(50), nullable=True)
