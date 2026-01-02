from sqlalchemy.orm import Session

from src.domain.entities.master_configuration_type import MasterConfigurationType
from src.domain.entities.file_configuration import FileConfiguration

class GetAllActiveFileListQueryBuilder:
    def __init__(self, db: Session, schematype: str | None = None, fileid: int | None = None):
        self.db = db
        # self.schema_type = schema_type
        self.schematype = schematype
        self.fileid = fileid
        self._query = None
    
    def build_query(self):
        """Build the query"""
        if self.schematype:
            self._query = self.db.query(FileConfiguration).filter(
                FileConfiguration.schematype == self.schematype,
                FileConfiguration.isactive == True
            ).order_by(FileConfiguration.fileid.desc()) # Order by Id DESC

        elif self.fileid:
            self._query = self.db.query(FileConfiguration).filter(
                FileConfiguration.fileid == self.fileid,
                FileConfiguration.isactive == True
            )
        else:
            self._query = self.db.query(FileConfiguration).filter(
                # FileConfiguration.schematype == self.schema_type,
                FileConfiguration.isactive == True  # Ensures the record is active
            ).order_by(FileConfiguration.fileid.desc())  # Order by Id DESC
        return self

    def build_query_master_config_type(self):
        """Build the query"""
        self._query = self.db.query(MasterConfigurationType).filter(
            MasterConfigurationType.type == "ContentType",
            MasterConfigurationType.isactive == True
        ).order_by(MasterConfigurationType.masterconfigurationtypeid) #Order by Id DESC
        return self
    
    def get_count(self) -> int:
        """Get total count of the results."""
        return self._query.count()
    
    def get_results(self):
        """Retrieve the results."""
        return self._query.all()
