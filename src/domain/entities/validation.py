import uuid
from sqlalchemy import Column, String, Boolean, Text, TIMESTAMP, Integer, BigInteger,DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from src.domain.entities.base_entity import BaseEntity

class Validation(BaseEntity):
    __tablename__ = "tbl_validation"
    __table_args__ = {'schema': 'frame'}

    validationid = Column(BigInteger, primary_key=True, autoincrement=True)
    accountsid = Column(BigInteger, nullable=True) # Changed to BigInteger to match ID
    fileuid = Column(UUID(as_uuid=True), nullable=False, default=uuid.uuid4)
    validationtype = Column(String(255))
    status = Column(String(255))
    description = Column(Text, nullable=True)
    difference = Column(DECIMAL)
    newportvalue = Column(DECIMAL)
    extractvalue = Column(DECIMAL)
    ismanuallyvalidate = Column(Boolean, default=False)
    validateBy = Column(String(255), default="SYSTEM")
    
    # isactive, created, createdby, updated, updatedby are inherited from BaseEntity
