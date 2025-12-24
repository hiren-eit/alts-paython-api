from sqlalchemy import Column, String, BigInteger, UUID, Numeric, Boolean, TIMESTAMP
from src.domain.entities.base_entity import BaseEntity
import uuid

class FileSecurityMapping(BaseEntity):
    """
    Entity representing security mapping for a file.
    Maps to tbl_file_security_mapping in the frame schema.
    Equivalent to DocumentSecurityMapping in .NET
    """
    __tablename__ = "tbl_file_security_mapping"
    __table_args__ = {'schema': 'frame'}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    fileuid = Column(UUID(as_uuid=True), nullable=False)
    security = Column(String(255), nullable=True)
    ticker = Column(String(100), nullable=True)
    cusip = Column(String(100), nullable=True)
    units = Column(Numeric(18, 2), nullable=True)
    lastprice = Column(Numeric(18, 2), nullable=True)
    marketvalue = Column(Numeric(18, 2), nullable=True)
    currency = Column(String(10), nullable=True)
    accruedinterest = Column(Numeric(18, 2), nullable=True)
    status = Column(String(50), nullable=True)
    comment = Column(String(500), nullable=True)
    ismissingsecurity = Column(Boolean, nullable=True)
    securitystage = Column(String(50), nullable=True)
    documentname = Column(String(255), nullable=True)
    # isactive, created, createdby, updated, updatedby are inherited from BaseEntity
