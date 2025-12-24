from sqlalchemy.orm import Session
from src.domain.interfaces.file_configure_repository_interface import IFileConfigurationRepository
from src.domain.dtos.document_configuration_dto import DocumentConfiguration
from uuid import UUID

class FileConfigurationService:

    def __init__(self, repository: IFileConfigurationRepository):
        self.repo = repository
    

    def get_all_active_file_configuration_list(self, db: Session):
        """
        Returns all active file configuration list with total count.
        Replicates the GetAllActiveDocumentConfigurationList stored procedure logic.
        """
        return self.repo.get_all_active_file_configuration_list(db)


    async def save_file_configuration(self, db: Session, documentConfiguration: DocumentConfiguration):
        """
        Add file configuration.
        Replicates the AddDocumentConfiguration stored procedure logic.
        """
        return await self.repo.save_file_configuration(db, documentConfiguration)

    
    async def update_file_configuration(self, db: Session, documentConfiguration: DocumentConfiguration):
        """
        Update file configuration.
        Replicates the UpdateDocumentConfiguration stored procedure logic.
        """
        return await self.repo.update_file_configuration(db, documentConfiguration)


    async def update_file_action_configuration(self, db: Session,documentConfiguration: DocumentConfiguration):
        """
        Update file configuration action.
        Replicates the UpdateDocumentConfigurationAction stored procedure logic.
        """
        return await self.repo.update_file_action_configuration(db, documentConfiguration)

    
    def get_file_configuration_by_id(self, db: Session, fileconfigurationid: int):
        """
        Returns file configuration by id.
        Replicates the GetDocumentConfigurationByID stored procedure logic.
        """
        return self.repo.get_file_configuration_by_id(db, fileconfigurationid)

    
    def get_file_configuration_type(self, db: Session):
        """
        Returns file configuration type.
        Replicates the GetDocumentConfigurationType stored procedure logic.
        """
        return self.repo.get_file_configuration_type(db)

    
    def get_file_configuration_by_schema_type(self, db: Session, schematype: str):
        """
        Returns document configuration by schema type.
        Replicates the GetDocumentConfigurationBySchemaType stored procedure logic.
        """
        return self.repo.get_file_configuration_by_schema_type(db, schematype)