import uuid
from sqlalchemy import Column, String, Boolean, Text, TIMESTAMP, Integer, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from src.domain.entities.base_entity import BaseEntity

class BusinessRule(BaseEntity):
    __tablename__ = "tbl_business_rule"
    __table_args__ = {'schema': 'frame'}

    businessruleid = Column(BigInteger, primary_key=True, autoincrement=True)
    sourceid = Column(BigInteger, nullable=True) # Changed to BigInteger to match MasterConfigurationType ID
    uniqueruleid = Column(String(255))
    ruletype = Column(String(50))
    ruleexpressions = Column(Text)
    password = Column(String(255))
    groupcode = Column(String(50))
    reasonfortoggle = Column(Text)
    documenttypeid = Column(BigInteger) # Changed to match MasterConfigurationType ID Refactor
    usage = Column(Integer, default=0) # Added based on C# GetBusinessDataResponse
    
    # isactive, created, createdby, updated, updatedby are inherited from BaseEntity
