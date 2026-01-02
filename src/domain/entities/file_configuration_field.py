from sqlalchemy import Column, String, BigInteger, ForeignKey, Boolean
from src.domain.entities.base_entity import BaseEntity


class FileConfigurationField(BaseEntity):
    """
    Entity representing a field configuration for a file type.
    Maps to tbl_file_configuration_field in the frame schema.
    """

    __tablename__ = "tbl_file_configuration_field"
    __table_args__ = {"schema": "frame"}

    fileconfigurationfieldid = Column(BigInteger, primary_key=True, autoincrement=True, name="fileid")
    # fileconfigurationid = Column(BigInteger, ForeignKey("frame.tbl_file_configuration.fileconfigurationid"))
    fileconfigurationid = Column(BigInteger, nullable=True)
    fieldname = Column(String(255), nullable=True)
    datatype = Column(String(50), nullable=True)
    description = Column(String(500), nullable=True)
    mandatory = Column(Boolean, nullable=True)
    parentfieldid = Column(BigInteger, nullable=True, name="parentfieldid")
