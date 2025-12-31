from sqlalchemy import TIMESTAMP, BigInteger, Column, DateTime, Boolean, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from uuid import uuid4

from src.infrastructure.database.base import Base


class BaseEntity(Base):
    __abstract__ = True

    created = Column(TIMESTAMP(7), nullable=False)
    createdby = Column(String(255), nullable=True)
    updated = Column(TIMESTAMP(7))
    updatedby = Column(String(255), nullable=True)
    isactive = Column(Boolean, nullable=False)
