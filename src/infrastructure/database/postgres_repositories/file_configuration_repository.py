import datetime
from typing import List, Any, Dict
from src.infrastructure.database.query_builders.get_all_active_file_list_result_enricher import GetAllActiveFileListResultEnricher
from src.infrastructure.database.query_builders.get_all_active_file_list_query_builder import GetAllActiveFileListQueryBuilder
from src.domain.entities.file_configuration_log import FileConfigurationLog
from src.infrastructure.database.query_builders.update_file_configuration_action_query_builder import UpdateFileConfigurationActionQueryBuilder
from src.core.settings import settings
from src.domain.dtos.resolve_file_update_dto import ResolveFileUpdate
from src.domain.entities.file_manager import FileManager

from sqlalchemy import true
from sqlalchemy.orm import Session

from sqlalchemy.orm import Session
from src.domain.entities.file_configuration_field import FileConfigurationField
from typing import List
from uuid import uuid4

from sqlalchemy.orm import Session
# import httpx
import json
from datetime import datetime

from src.domain.entities.file_configuration import FileConfiguration
from src.infrastructure.database.query_builders import save_file_configuration_query_builder
from src.infrastructure.database.query_builders.update_file_configuration_query_builder import UpdateFileConfiguration
from src.domain.interfaces.file_configure_repository_interface import IFileConfigurationRepository
from src.domain.dtos.file_configuration_dto import FileConfiguration as FileConfigurationDTO, FileConfigurationField
from src.infrastructure.database.query_builders.save_file_configuration_query_builder import SaveFileConfigurationQueryBuilder
from src.infrastructure.logging.logger_manager import get_logger
from uuid import UUID
logger = get_logger(__name__)

class FileConfigurationRepository(IFileConfigurationRepository):
    "SQL Server implementation of FileConfiguration repository using SQLAlchemy ORM"


    def get_all_active_file_configuration_list(self, db: Session) -> Dict:
        """
        Returns all active file configuration list with total count.

        Returns:
                dict: {
                    "result_code": "SUCCESS",
                    "total": int,
                    # "in_review_count": int,
                    "data": List[FileConfiguration]
                }
        """
        try:
            logger.info("GetAllActiveFileConfigurationList")

            # Build query to get all active FileConfigurations
            query_builder = GetAllActiveFileListQueryBuilder(db)
            query_builder.build_query()
            
            # Fetch the results
            results = query_builder.get_results()

            #Get the count of the result
            count = query_builder.get_count()

            # Enrich the results (add additional details)
            result_enricher = GetAllActiveFileListResultEnricher(db)
            enriched_result = result_enricher.enrich(results)

            return {
                "result_code": "SUCCESS",
                "total": count,
                # "in_review_count": 1,
                "data": enriched_result
            }
        except Exception as ex:
            logger.error(f"GetAllActiveFileConfigurationList error: {ex}", exc_info=True)
            db.rollback()
            raise

    
    async def save_file_configuration(self, db: Session, fileConfiguration: FileConfigurationDTO) -> bool:
        """
        Add file configuration.
        Replicates the AddFileConfiguration stored procedure logic.
        """
        try:
            logger.info("AddFileConfiguration")
            query_builder = SaveFileConfigurationQueryBuilder(db)
            if query_builder.configuration_exists(fileConfiguration.configuration_name):
                return False

            configuration, fields_count = query_builder.create_file_with_fields(
                fileConfiguration
            )

            query_builder.save_log(
                configuration.fileid,
                fields_count,
                fileConfiguration.created_by,
            )

            query_builder.commit()
            await self._send_to_external_api(configuration)

            logger.info("FileConfiguration saved and sent externally")
            return True

        except Exception as ex:
            db.rollback()
            logger.exception(
                "Error inserting FileConfiguration and related entities"
            )
            raise


    async def update_file_configuration(self, db: Session, fileConfiguration: FileConfigurationDTO) -> bool:
        """
            Update file configuration.
            Replicates the UpdateFileConfiguration stored procedure logic.
        """
        try:
            logger.info("UpdateFileConfiguration")
            query_builder = UpdateFileConfiguration(db)
            
            existing_config = query_builder.get_file_configuration(fileConfiguration.fileid)
            if not existing_config:
                return False

            # 2. Log changes and update fields
            changes = []
            if existing_config.description != fileConfiguration.description:
                changes.append({
                    "field_name": "description",
                    "description": f"Description changed from {existing_config.description} to {fileConfiguration.description}",
                    "change_type": "Updated"
                })
                existing_config.description = fileConfiguration.description

            if existing_config.sla_priority != fileConfiguration.sla_priority:
                changes.append({
                    "field_name": "sla_priority",
                    "description": f"SLA Priority changed from {existing_config.sla_priority} to {fileConfiguration.sla_priority}",
                    "change_type": "Updated"
                })
                existing_config.sla_priority = fileConfiguration.sla_priority

                
            if existing_config.sla_days != fileConfiguration.sla_days:
                changes.append({
                    "field_name": "sla_days",
                    "description": f"SLA Days changed from {existing_config.sla_days} to {fileConfiguration.sla_days}",
                    "change_type": "Updated"
                })
                existing_config.sla_days = fileConfiguration.sla_days

            if existing_config.schematype != fileConfiguration.schema_type:
                changes.append({
                    "field_name": "schematype",
                    "description": f"Schematype changed from {existing_config.schematype} to {fileConfiguration.schema_type}",
                    "change_type": "Updated"
                })
                existing_config.schematype = fileConfiguration.schema_type

            if existing_config.extraction != fileConfiguration.extraction:
                changes.append({
                    "field_name": "extraction",
                    "description": f"Extraction changed from {existing_config.extraction} to {fileConfiguration.extraction}",
                    "change_type": "Updated"
                })
                existing_config.extraction = fileConfiguration.extraction

            if existing_config.fieldtype != fileConfiguration.field_type:
                changes.append({
                    "field_name": "fieldtype",
                    "description": f"Field Type changed from {existing_config.fieldtype} to {fileConfiguration.field_type}",
                    "change_type": "Updated"
                })
                existing_config.fieldtype = fileConfiguration.field_type

            # 3. Update the configuration in DB
            query_builder.update_configuration(existing_config, updated_by=fileConfiguration.updated_by or "SYSTEM")

            # 4. Create change log
            if changes:
                log_payload = json.dumps([{"description": change, "changeType": "Updated"} for change in changes])
                query_builder.save_log(existing_config.fileid, log_payload, fileConfiguration.created_by)

            # 5. Commit transaction
            query_builder.commit()

            # 6. Send the updated configuration to external API
            await self._send_to_external_api(existing_config)

            return True
        except Exception as ex:
            logger.error(f"UpdateFileConfiguration error: {ex}", exc_info=True)
            query_builder.rollback()
            raise

    
    async def update_file_action_configuration(self, db: Session, fileConfiguration: FileConfigurationDTO) -> bool:
        """
            Update file configuration action.
            Replicates the UpdateFileConfigurationAction stored procedure logic.
        """
        try:
            logger.info("UpdateFileConfigurationAction")
            query_builder = UpdateFileConfigurationActionQueryBuilder(db)
            file_config_result = query_builder.get_file_configuration(fileConfiguration.fileid)
            if not file_config_result:
                logger.error(f"File Configuration with ID {fileConfiguration.fileid} not found")
                return False

            changes = []

            if file_config_result.isactive != fileConfiguration.is_active:
                changes.append({
                    "field_name": "isactive",
                    "description": f"{fileConfiguration.reason}",
                    "change_type": "Updated"
                })
                file_config_result.isactive = fileConfiguration.is_active

            file_config_result.reason = fileConfiguration.reason
            file_config_result.updated = datetime.utcnow()
            file_config_result.updatedby = fileConfiguration.updated_by

            query_builder.update_file_configuration_in_db()

            #Log changes if any
            if changes:
                json_description = json.dumps(changes)
                log_entry = FileConfigurationLog(
                    fileconfigurationid = fileConfiguration.fileid,
                    title="Configuration Activated" if fileConfiguration.is_active else "Configuration Deactivated",
                    description=json_description,
                    updated=datetime.utcnow(),
                    updatedby=fileConfiguration.updated_by or "SYSTEM",
                    created=datetime.utcnow(),
                    createdby=fileConfiguration.created_by or "SYSTEM",
                    isactive=True if fileConfiguration.is_active else False,
                )
                query_builder.save_log(log_entry)

                updated_file = query_builder.get_file_configuration(fileConfiguration.fileid)

                # json_payload = json.dumps({
                #     "id": updated_file.fileid,
                #     "configuration_name": updated_file.configurationname,
                #     "description": updated_file.description,
                #     "sla_priority": updated_file.sla_priority,
                #     "sla_days": updated_file.sla_days,
                #     "schema_type": updated_file.schematype,
                #     "extraction": updated_file.extraction,
                #     "file_type_id": str(updated_file.filetypeid),
                #     "is_active": updated_file.isactive,
                #     "fields_collection": fileConfiguration.fields_collection
                # })
                
                # await self._send_to_external_api(json_payload)

            return True
        except Exception as ex:
            logger.error(f"UpdateFileConfigurationAction error: {ex}", exc_info=True)
            db.rollback()
            raise

    
    def get_file_configuration_by_id(self, db: Session, fileconfigurationid: int) -> Dict:
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
        try:
            logger.info("GetFileConfigurationByID")
            logger.info("GetFileConfigurationBySchemaType")
            # Build query to get all active FileConfigurations
            query_builder = GetAllActiveFileListQueryBuilder(db, fileid=fileconfigurationid)
            query_builder.build_query()
            
            # Fetch the results
            results = query_builder.get_results()

            #Get the count of the result
            count = query_builder.get_count()

            # Enrich the results (add additional details)
            result_enricher = GetAllActiveFileListResultEnricher(db)
            enriched_result = result_enricher.enrich(results)

            return {
                "result_code": "SUCCESS",
                "total": count,
                # "in_review_count": 1,
                "data": enriched_result
            }
        except Exception as ex:
            logger.error(f"GetFileConfigurationByID error: {ex}", exc_info=True)
            db.rollback()
            raise

    
    def get_file_configuration_type(self, db: Session) -> Dict:
        """
            Returns file configuration type.
            Replicates the GetFileConfigurationType stored procedure logic.
            
            Returns:
                dict: {
                    "result_code": "SUCCESS",
                    "total": int,
                    "in_review_count": int,
                    "data": List[FileConfiguration]
                }
        """
        try:
            logger.info("GetFileConfigurationType")
            # Build query to get all active FileConfigurations
            query_builder = GetAllActiveFileListQueryBuilder(db)
            query_builder.build_query_master_config_type()
            
            # Fetch the results
            results = query_builder.get_results()

            #Get the count of the result
            count = query_builder.get_count()

            # Enrich the results (add additional details)
            result_enricher = GetAllActiveFileListResultEnricher(db)
            enriched_result = result_enricher.enrich_master_config_type(results)

            return {
                "result_code": "SUCCESS",
                "total": count,
                # "in_review_count": 1,
                "data": enriched_result
            }
        except Exception as ex:
            logger.error(f"GetFileConfigurationType error: {ex}", exc_info=True)
            db.rollback()
            raise


    def get_file_configuration_by_schema_type(self, db: Session, schematype: str) -> Dict:
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
        try:
            logger.info("GetFileConfigurationBySchemaType")
            # Build query to get all active FileConfigurations
            query_builder = GetAllActiveFileListQueryBuilder(db, schematype)
            query_builder.build_query()
            
            # Fetch the results
            results = query_builder.get_results()

            #Get the count of the result
            count = query_builder.get_count()

            # Enrich the results (add additional details)
            result_enricher = GetAllActiveFileListResultEnricher(db)
            enriched_result = result_enricher.enrich(results)

            return {
                "result_code": "SUCCESS",
                "total": count,
                # "in_review_count": 1,
                "data": enriched_result
            }
        except Exception as ex:
            logger.error(f"GetFileConfigurationBySchemaType error: {ex}", exc_info=True)
            db.rollback()
            raise

    def _add_sub_rows_recursive(
        self,
        field_dto: FileConfigurationField,
        file_configuration_id: int,
        parent_field: FileConfigurationField,
        accumulator: List[FileConfigurationField],
    ):
        child_field = FileConfigurationField(
            fieldname=field_dto.field_name,
            datatype=field_dto.data_type,
            description=field_dto.description,
            mandatory=field_dto.mandatory,
            fileconfigurationid=file_configuration_id,
            parentfieldid=None,  # set after flush
            created=field_dto.created,
            createdby=field_dto.created_by,
            isactive=True,
        )

        self.db.add(child_field)
        self.db.flush()  # ensures PK is generated

        child_field.parentfieldid = parent_field.fileid
        accumulator.append(child_field)

        if (
            field_dto.data_type in ("Array", "Object")
            and field_dto.sub_rows
        ):
            for sub_row in field_dto.sub_rows:
                self._add_sub_rows_recursive(
                    sub_row,
                    file_configuration_id,
                    child_field,
                    accumulator,
                )

    # def resolve_file_update(
    #     self,
    #     db: Session,
    #     resolveUpdate: ResolveFileUpdate,
    # ) -> Dict:
    #     """
    #         Resolves file update..
            
    #         Returns:
    #             dict: {
    #                 "result_code": "SUCCESS",
    #                 "total": int,
    #                 "data": List[FileConfiguration]
    #             }
    #     """
    #     try:
    #         logger.info("ResolveFileUpdate")

    #         selected_file = (
    #             db.query(FileManager)
    #             .filter(
    #                 FileManager.fileuid == resolveUpdate.selected_file_uid,
    #                 FileManager.isactive.is_(True)
    #             )
    #             .first()
    #         )

    #         ignored_file = (
    #             db.query(FileManager)
    #             .filter(
    #                 FileManager.fileuid == resolveUpdate.ignored_file_uid,
    #                 FileManager.isactive.is_(True)
    #             )
    #             .first()
    #         )

    #         if selected_file is None or ignored_file is None:
    #             result_code = "Error"
    #             result_message = "One or both files are not found."
            
    #         with db.begin():
    #             if selected_file.status == "Update":
    #                 if ignored_file.status == "Ingested" or ignored_file.status == "Completed":
    #                     return {
    #                         "result_code": "Error",
    #                         "result_message": (f"Earlier file {ignored_file.fileuid}, {ignored_file.filename} already ingested. "
    #                                         "This action will not ingest the updated file. "
    #                                         "You may make changes to the existing position/transaction directly.")
    #                     }

    #         return {
    #             "result_code": result_code,
    #             # "total": count,
    #             # "in_review_count": 1,
    #             # "data": enriched_result,
    #             "result_message": result_message
    #         }
    #     except Exception as ex:
    #         logger.error(f"ResolveFileUpdate error: {ex}", exc_info=True)
    #         db.rollback()
    #         raise
    
    async def _send_to_external_api(self, payload: dict):
        # headers = {
        #     "Ocp-Apim-Subscription-Key": settings.subscription_key,
        #     "Integrator-Key": settings.integrator_key,
        #     "Content-Type": "application/json",
        # }
        headers = {}

        # async with httpx.AsyncClient(timeout=30) as client:
        #     response = await client.post(
        #         settings.EXTERNAL_API_URL,
        #         json=payload,
        #         headers=headers,
        #     )

        #     if response.status_code >= 400:
        #         logger.error(
        #             f"External API call failed: {response.status_code} - {response.text}"
        #         )