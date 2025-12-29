from typing import List, Any, Dict
from sqlalchemy.orm import Session
from src.domain.dtos.file_configuration_dto import FileConfiguration
from uuid import UUID

class IFileConfigurationRepository:
    """Repository interface for FileConfiguration"""

    def get_all_active_file_configuration_list(
        self, 
        db: Session
    ) -> Dict:
        """
        Returns all active file configuration list with total count.
        Replicates the GetAllActiveFileConfigurationList stored procedure logic.
        
        Returns:
                dict: {
                    "result_code": "SUCCESS",
                    "total": int,
                    "in_review_count": int,
                    "data": List[FileConfiguration]
                }
        """
        raise NotImplementedError


    async def save_file_configuration(
        self,
        db: Session,
        fileConfiguration: FileConfiguration
    ) -> bool:
        """
        Add file configuration.
        Replicates the AddFileConfiguration stored procedure logic.
        """
        raise NotImplementedError


    async def update_file_configuration(
        self,
        db: Session,
        fileConfiguration: FileConfiguration
    ) -> bool:
        """
        Update file configuration.
        Replicates the UpdateFileConfiguration stored procedure logic.
        """
        raise NotImplementedError


    async def update_file_action_configuration(
        self,
        db: Session,
        fileConfiguration: FileConfiguration
    ) -> bool:
        """
        Update file configuration action.
        Replicates the UpdateFileConfigurationAction stored procedure logic.
        """
        raise NotImplementedError

    
    def get_file_configuration_by_id(
        self,
        db: Session,
        fileconfigurationid: int
    ) -> Dict:
        """
        Returns file configuration by id.
        Replicates the GetFileConfigurationByID stored procedure logic.
        
        Returns:
                dict: {
                    "result_code": "SUCCESS",
                    "total": int,
                    "data": List[FileConfiguration]
                }
        """
        raise NotImplementedError

    
    def get_file_configuration_type(
        self,
        db: Session,
    ) -> Dict:
        """
        Returns file configuration type.
        Replicates the GetFileConfigurationType stored procedure logic.
        
        Returns:
                dict: {
                    "result_code": "SUCCESS",
                    "total": int,
                    "data": List[FileConfiguration]
                }
        """
        raise NotImplementedError

    
    def get_file_configuration_by_schema_type(
        self,
        db: Session,
        schematype: str
    ) -> Dict:
        """
        Returns file configuration by schema type.
        Replicates the GetFileConfigurationBySchemaType stored procedure logic.
        
        Returns:
                dict: {
                    "result_code": "SUCCESS",
                    "total": int,
                    "data": List[FileConfiguration]
                }
        """
        raise NotImplementedError