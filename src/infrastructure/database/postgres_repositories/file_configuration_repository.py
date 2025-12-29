import datetime
from typing import List, Any, Dict
from src.infrastructure.database.query_builders.get_all_active_document_list_result_enricher import GetAllActiveDocumentListResultEnricher
from src.infrastructure.database.query_builders.get_all_active_document_list_query_builder import GetAllActiveDocumentListQueryBuilder
from src.domain.entities.file_configuration_log import FileConfigurationLog
from src.infrastructure.database.query_builders.update_document_configuration_action_query_builder import UpdateDocumentConfigurationActionQueryBuilder
from src.core.settings import settings

from sqlalchemy import true
from sqlalchemy.orm import Session

from sqlalchemy.orm import Session
from src.domain.entities.file_configuration_field import FileConfigurationField
from typing import List
from uuid import uuid4

from sqlalchemy.orm import Session
import httpx
import json
from datetime import datetime

from src.domain.entities.file_configuration import FileConfiguration
from src.infrastructure.database.query_builders import save_document_configuration_query_builder
from src.infrastructure.database.query_builders.update_document_configuration_query_builder import UpdateDocumentConfiguration
from src.domain.interfaces.file_configure_repository_interface import IFileConfigurationRepository
# from src.infrastructure.database.query_builders.save_document_configuration_query_builder import DocumentConfigurationQueryBuilder
# from src.infrastructure.database.query_builders.save_document_configuration_result_enricher import DocumentConfigurationResultEnricher
from src.domain.dtos.file_configuration_dto import FileConfiguration, FileConfigurationField
from src.infrastructure.database.query_builders.save_document_configuration_query_builder import SaveDocumentConfigurationQueryBuilder
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
                    "data": List[DocumentConfiguration]
                }
        """
        try:
            logger.info("GetAllActiveDocumentConfigurationList")

            # Build query to get all active FileConfigurations
            query_builder = GetAllActiveDocumentListQueryBuilder(db)
            query_builder.build_query()
            
            # Fetch the results
            results = query_builder.get_results()

            #Get the count of the result
            count = query_builder.get_count()

            # Enrich the results (add additional details)
            result_enricher = GetAllActiveDocumentListResultEnricher(db)
            enriched_result = result_enricher.enrich(results)

            return {
                "result_code": "SUCCESS",
                "total": count,
                # "in_review_count": 1,
                "data": enriched_result
            }
        except Exception as ex:
            logger.error(f"GetAllActiveDocumentConfigurationList error: {ex}", exc_info=True)
            db.rollback()
            raise

    
    async def save_file_configuration(self, db: Session, documentConfiguration: FileConfiguration) -> bool:
        """
        Add file configuration.
        Replicates the AddDocumentConfiguration stored procedure logic.
        """
        try:
            logger.info("AddDocumentConfiguration")
            query_builder = SaveDocumentConfigurationQueryBuilder(db)
            if query_builder.configuration_exists(documentConfiguration.configuration_name):
                return False

            configuration, fields_count = query_builder.create_document_with_fields(
                documentConfiguration
            )

            query_builder.save_log(
                configuration.fileid,
                fields_count,
                len(documentConfiguration.created_by),
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


    async def update_file_configuration(self, db: Session, documentConfiguration: FileConfiguration) -> bool:
        """
            Update file configuration.
            Replicates the UpdateDocumentConfiguration stored procedure logic.
        """
        try:
            logger.info("UpdateDocumentConfiguration")
            query_builder = UpdateDocumentConfiguration(db)
            
            existing_config = query_builder.get_document_configuration(documentConfiguration.fileid)
            if not existing_config:
                return False

            # 2. Log changes and update fields
            changes = []
            if existing_config.description != documentConfiguration.description:
                changes.append({
                    "field_name": "description",
                    "description": f"Description changed from {existing_config.description} to {documentConfiguration.description}",
                    "change_type": "Updated"
                })
                existing_config.description = documentConfiguration.description

            if existing_config.sla_priority != documentConfiguration.sla_priority:
                changes.append({
                    "field_name": "sla_priority",
                    "description": f"SLA Priority changed from {existing_config.sla_priority} to {documentConfiguration.sla_priority}",
                    "change_type": "Updated"
                })
                existing_config.sla_priority = documentConfiguration.sla_priority

                
            if existing_config.sla_days != documentConfiguration.sla_days:
                changes.append({
                    "field_name": "sla_days",
                    "description": f"SLA Days changed from {existing_config.sla_days} to {documentConfiguration.sla_days}",
                    "change_type": "Updated"
                })
                existing_config.sla_days = documentConfiguration.sla_days

            if existing_config.schematype != documentConfiguration.schema_type:
                changes.append({
                    "field_name": "schematype",
                    "description": f"Schematype changed from {existing_config.schematype} to {documentConfiguration.schema_type}",
                    "change_type": "Updated"
                })
                existing_config.schematype = documentConfiguration.schema_type

            if existing_config.extraction != documentConfiguration.extraction:
                changes.append({
                    "field_name": "extraction",
                    "description": f"Extraction changed from {existing_config.extraction} to {documentConfiguration.extraction}",
                    "change_type": "Updated"
                })
                existing_config.extraction = documentConfiguration.extraction

            if existing_config.fieldtype != documentConfiguration.field_type:
                changes.append({
                    "field_name": "fieldtype",
                    "description": f"Field Type changed from {existing_config.fieldtype} to {documentConfiguration.field_type}",
                    "change_type": "Updated"
                })
                existing_config.fieldtype = documentConfiguration.field_type

            # 3. Update the configuration in DB
            query_builder.update_configuration(existing_config, updated_by=documentConfiguration.updated_by)

            # 4. Create change log
            if changes:
                log_payload = json.dumps([{"description": change, "changeType": "Updated"} for change in changes])
                query_builder.save_log(existing_config.fileid, log_payload, len(documentConfiguration.created_by))

            # 5. Commit transaction
            query_builder.commit()

            # 6. Send the updated configuration to external API
            await self._send_to_external_api(existing_config)

            return True
        except Exception as ex:
            logger.error(f"UpdateDocumentConfiguration error: {ex}", exc_info=True)
            query_builder.rollback()
            raise

    
    async def update_file_action_configuration(self, db: Session, documentConfiguration: FileConfiguration) -> bool:
        """
            Update file configuration action.
            Replicates the UpdateDocumentConfigurationAction stored procedure logic.
        """
        try:
            logger.info("UpdateDocumentConfigurationAction")
            query_builder = UpdateDocumentConfigurationActionQueryBuilder(db)
            document_config_result = query_builder.get_document_configuration(documentConfiguration.fileid)
            if not document_config_result:
                logger.error(f"Document Configuration with ID {documentConfiguration.fileid} not found")
                return False

            changes = []

            if document_config_result.isactive != documentConfiguration.is_active:
                changes.append({
                    "field_name": "isactive",
                    "description": f"{documentConfiguration.reason}",
                    "change_type": "Updated"
                })
                document_config_result.isactive = documentConfiguration.is_active

            document_config_result.reason = documentConfiguration.reason
            document_config_result.updated = datetime.utcnow()
            document_config_result.updatedby = len(documentConfiguration.updated_by or "SYSTEM")

            query_builder.update_document_configuration_in_db()

            #Log changes if any
            if changes:
                json_description = json.dumps(changes)
                log_entry = FileConfigurationLog(
                    fileconfigurationid = documentConfiguration.fileid,
                    title="Configuration Activated" if documentConfiguration.is_active else "Configuration Deactivated",
                    description=json_description,
                    updated=datetime.utcnow(),
                    updatedby=len(documentConfiguration.updated_by or "SYSTEM"),
                    created=datetime.utcnow(),
                    createdby=len(documentConfiguration.created_by or "SYSTEM"),
                    isactive=True if documentConfiguration.is_active else False,
                )
                query_builder.save_log(log_entry)

                updated_document = query_builder.get_document_configuration(documentConfiguration.fileid)

                # json_payload = json.dumps({
                #     "id": updated_document.fileid,
                #     "configuration_name": updated_document.configurationname,
                #     "description": updated_document.description,
                #     "sla_priority": updated_document.sla_priority,
                #     "sla_days": updated_document.sla_days,
                #     "schema_type": updated_document.schematype,
                #     "extraction": updated_document.extraction,
                #     "document_type_id": str(updated_document.filetypeid),
                #     "is_active": updated_document.isactive,
                #     "fields_collection": documentConfiguration.fields_collection
                # })
                
                # await self._send_to_external_api(json_payload)

            return True
        except Exception as ex:
            logger.error(f"UpdateDocumentConfigurationAction error: {ex}", exc_info=True)
            db.rollback()
            raise

    
    def get_file_configuration_by_id(self, db: Session, fileconfigurationid: int) -> Dict:
        """
            Returns file configuration by id.
            Replicates the GetDocumentConfigurationByID stored procedure logic.
            
            Returns:
                dict: {
                    "result_code": "SUCCESS",
                    "total": int,
                    "data": List[DocumentConfiguration]
                }
        """
        try:
            logger.info("GetDocumentConfigurationByID")
            logger.info("GetDocumentConfigurationBySchemaType")
            # Build query to get all active FileConfigurations
            query_builder = GetAllActiveDocumentListQueryBuilder(db, fileid=fileconfigurationid)
            query_builder.build_query()
            
            # Fetch the results
            results = query_builder.get_results()

            #Get the count of the result
            count = query_builder.get_count()

            # Enrich the results (add additional details)
            result_enricher = GetAllActiveDocumentListResultEnricher(db)
            enriched_result = result_enricher.enrich(results)

            return {
                "result_code": "SUCCESS",
                "total": count,
                # "in_review_count": 1,
                "data": enriched_result
            }
        except Exception as ex:
            logger.error(f"GetDocumentConfigurationByID error: {ex}", exc_info=True)
            db.rollback()
            raise

    
    def get_file_configuration_type(self, db: Session) -> Dict:
        """
            Returns file configuration type.
            Replicates the GetDocumentConfigurationType stored procedure logic.
            
            Returns:
                dict: {
                    "result_code": "SUCCESS",
                    "total": int,
                    "in_review_count": int,
                    "data": List[DocumentConfiguration]
                }
        """
        try:
            logger.info("GetDocumentConfigurationType")
            # Build query to get all active FileConfigurations
            query_builder = GetAllActiveDocumentListQueryBuilder(db)
            query_builder.build_query_master_config_type()
            
            # Fetch the results
            results = query_builder.get_results()

            #Get the count of the result
            count = query_builder.get_count()

            # Enrich the results (add additional details)
            result_enricher = GetAllActiveDocumentListResultEnricher(db)
            enriched_result = result_enricher.enrich_master_config_type(results)

            return {
                "result_code": "SUCCESS",
                "total": count,
                # "in_review_count": 1,
                "data": enriched_result
            }
        except Exception as ex:
            logger.error(f"GetDocumentConfigurationType error: {ex}", exc_info=True)
            db.rollback()
            raise


    def get_file_configuration_by_schema_type(self, db: Session, schematype: str) -> Dict:
        """
            Returns document configuration by schema type.
            Replicates the GetDocumentConfigurationBySchemaType stored procedure logic.
            
            Returns:
                dict: {
                    "result_code": "SUCCESS",
                    "total": int,
                    "data": List[DocumentConfiguration]
                }
        """
        try:
            logger.info("GetDocumentConfigurationBySchemaType")
            # Build query to get all active FileConfigurations
            query_builder = GetAllActiveDocumentListQueryBuilder(db, schematype)
            query_builder.build_query()
            
            # Fetch the results
            results = query_builder.get_results()

            #Get the count of the result
            count = query_builder.get_count()

            # Enrich the results (add additional details)
            result_enricher = GetAllActiveDocumentListResultEnricher(db)
            enriched_result = result_enricher.enrich(results)

            return {
                "result_code": "SUCCESS",
                "total": count,
                # "in_review_count": 1,
                "data": enriched_result
            }
        except Exception as ex:
            logger.error(f"GetDocumentConfigurationBySchemaType error: {ex}", exc_info=True)
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
    
    async def _send_to_external_api(self, payload: dict):
        headers = {
            "Ocp-Apim-Subscription-Key": settings.subscription_key,
            "Integrator-Key": settings.integrator_key,
            "Content-Type": "application/json",
        }

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