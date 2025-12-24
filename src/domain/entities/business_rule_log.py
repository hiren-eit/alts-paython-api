import uuid
from sqlalchemy import Column, String, Text, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from src.domain.entities.base_entity import BaseEntity

class BusinessRuleLog(BaseEntity):
    __tablename__ = "tbl_business_rule_log"
    __table_args__ = {'schema': 'frame'}

    businessrulelogid = Column(BigInteger, primary_key=True, autoincrement=True)
    uniqueruleid = Column(String(255))
    changetype = Column(String(50))
    ruleexpressions = Column(Text)
    rulelogmessage = Column(Text)
    rulelogtitle = Column(String(255))
    
    # created, createdby, updated, updatedby, isactive are inherited from BaseEntity
