from sqlalchemy.orm import Session
from src.domain.interfaces.file_configure_repository_interface import IFileConfigurationRepository
from src.domain.dtos.file_configuration_dto import FileConfiguration
from uuid import UUID

class FileConfigurationService:

    def __init__(self, repository: IFileConfigurationRepository):
        self.repo = repository
    

    def get_all_active_file_configuration_list(self, db: Session):
        """
        Returns all active file configuration list with total count.
        Replicates the GetAllActiveFileConfigurationList stored procedure logic.
        """
        return self.repo.get_all_active_file_configuration_list(db)


    async def save_file_configuration(self, db: Session, fileConfiguration: FileConfiguration):
        """
        Add file configuration.
        Replicates the AddFileConfiguration stored procedure logic.
        """
        return await self.repo.save_file_configuration(db, fileConfiguration)

    
    async def update_file_configuration(self, db: Session, fileConfiguration: FileConfiguration):
        """
        Update file configuration.
        Replicates the UpdateFileConfiguration stored procedure logic.
        """
        return await self.repo.update_file_configuration(db, fileConfiguration)


    async def update_file_action_configuration(self, db: Session,fileConfiguration: FileConfiguration):
        """
        Update file configuration action.
        Replicates the UpdateFileConfigurationAction stored procedure logic.
        """
        return await self.repo.update_file_action_configuration(db, fileConfiguration)

    
    def get_file_configuration_by_id(self, db: Session, fileconfigurationid: int):
        """
        Returns file configuration by id.
        Replicates the GetFileConfigurationByID stored procedure logic.
        """
        return self.repo.get_file_configuration_by_id(db, fileconfigurationid)

    
    def get_file_configuration_type(self, db: Session):
        """
        Returns file configuration type.
        Replicates the GetFileConfigurationType stored procedure logic.
        """
        return self.repo.get_file_configuration_type(db)

    
    def get_file_configuration_by_schema_type(self, db: Session, schematype: str):
        """
        Returns file configuration by schema type.
        Replicates the GetFileConfigurationBySchemaType stored procedure logic.
        """
        return self.repo.get_file_configuration_by_schema_type(db, schematype)