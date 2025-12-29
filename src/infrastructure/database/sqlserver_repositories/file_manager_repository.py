"""
SQL Server File Manager Repository
Uses the same query builders as PostgreSQL since SQLAlchemy ORM is database-agnostic.
"""
from typing import List, Any, Dict
from sqlalchemy.orm import Session
from src.domain.interfaces.file_manager_repository_interface import IFileManagerRepository
from src.domain.dtos.file_manager_dto import FileManagerFilter
from src.domain.dtos.update_extract_file_dto import UpdateExtractFileRequest, ResponseObjectModel
from src.infrastructure.database.query_builders import (
    DocumentManagerQueryBuilder,
    DocumentManagerResultEnricher
)
from src.infrastructure.database.query_builders.file_details_query_builder import DocumentDetailsQueryBuilder
from src.infrastructure.database.query_builders.file_details_result_enricher import DocumentDetailsResultEnricher
from src.domain.dtos.file_details_dto import DocumentDetailsResponse
from src.infrastructure.logging.logger_manager import get_logger
from src.domain.dtos.extract_file_dto import (
    ExtractionDocumentField,
    ExtractionFileDetailDTO,
    FileConfigurationFieldDTO,
    FileSecurityMappingDTO
)
from uuid import UUID

logger = get_logger(__name__)


class FileManagerRepository(IFileManagerRepository):
    """SQL Server implementation of FileManager repository using SQLAlchemy ORM"""

    def get_file_manager_list(
        self, 
        db: Session, 
        filters: FileManagerFilter
    ) -> Dict:
        """
        Replicates GetDocumentManager stored procedure logic.
        Uses SQLAlchemy ORM - same code works for both PostgreSQL and SQL Server.
        """
        try:
            logger.info(f"GetFileManagerList: status={filters.document_status}, docType={filters.doc_type}")
            
            # Build query with all filters
            query_builder = DocumentManagerQueryBuilder(db, filters)
            query_builder.build_query()
            
            # Get count and results
            total_count = query_builder.get_count()
            results = query_builder.get_results()
            
            # Enrich results with account info and SLA calculations
            enricher = DocumentManagerResultEnricher(db, filters)
            items = enricher.enrich(results)
            
            logger.info(f"GetFileManagerList: returned {len(items)} items, total={total_count}")
            
            return {
                "total": total_count,
                "page": filters.page_number,
                "page_size": filters.page_size,
                "data": items
            }
            
        except Exception as ex:
            logger.error(f"GetFileManagerList error: {ex}", exc_info=True)
            raise

    def get_file_details_by_file_uid(
        self,
        db: Session,
        fileuid: UUID
    ) -> DocumentDetailsResponse:
        """
        Replicates GetDocumentDetailsByDocUID stored procedure logic.
        Uses separated QueryBuilder and ResultEnricher for clean code.
        """
        try:
            logger.info(f"GetDocumentDetailsByDocUID: fileuid={fileuid}")

            # 1. Build query
            query_builder = DocumentDetailsQueryBuilder(db, str(fileuid))
            query_builder.build_query()
            
            # 2. Fetch raw DB record (single row)
            result = query_builder.get_one()
            
            if not result:
                logger.info(f"GetDocumentDetailsByDocUID: No document found for {fileuid}")
                return {
                    "total": 0,
                    "page": 1,
                    "page_size": 1,
                    "data": []
                }

            # 3. Enrich result
            enricher = DocumentDetailsResultEnricher(db)
            enriched = enricher.enrich(result)

            logger.info(f"GetDocumentDetailsByDocUID: returning details for {fileuid}")
            
            # Wrap in paginated structure to match likely API requirements
            return {
                "total": 1,
                "data": [enriched]
            }

        except Exception as ex:
            logger.error(f"GetDocumentDetailsByDocUID error: {ex}", exc_info=True)
            raise
        
    def get_manual_extraction_config_fields_by_id(
        self,
        db: Session,
        documentConfigurationId: int
    ):
        """
        Replicates GetManualExtractionConfigFieldsById stored procedure logic.
        Queries configuration and its associated 'Object' type fields.
        """
        try:
            from src.domain.entities.file_configuration import FileConfiguration
            from src.domain.entities.file_configuration_field import FileConfigurationField

            logger.info(f"GetManualExtractionConfigFieldsById: id={documentConfigurationId}")

            # 1. Verify Configuration exists and is active
            config = db.query(FileConfiguration).filter(
                FileConfiguration.fileconfigurationid == documentConfigurationId,
                FileConfiguration.isactive == True
            ).first()

            if not config:
                logger.warning(f"GetManualExtractionConfigFieldsById: Configuration {documentConfigurationId} not found or inactive")
                return {
                    "count": 0,
                    "resultobject": [],
                    "resultcode": "NOT_FOUND"
                }

            # 2. Get Fields where DataType is 'Object'
            fields = db.query(FileConfigurationField).filter(
                FileConfigurationField.fileconfigurationid == documentConfigurationId,
                FileConfigurationField.isactive == True,
                FileConfigurationField.datatype == 'Object'
            ).all()

            # Map to DTO-like list for response
            result_list = []
            for f in fields:
                result_list.append({
                    "fileconfigurationfieldid": f.fileconfigurationfieldid,
                    "fileconfigurationid": f.fileconfigurationid,
                    "name": f.name,
                    "datatype": f.datatype,
                    "isactive": f.isactive
                })

            return {
                "count": len(result_list),
                "resultobject": result_list,
                "resultcode": "SUCCESS"
            }

        except Exception as ex:
            logger.error(f"GetManualExtractionConfigFieldsById error: {ex}", exc_info=True)
            raise

    def get_extract_document_api(
        self,
        db: Session,
        fileuid: UUID
    ):
        """
        Replicates GetExtractDocumentApi logic from .NET.
        Returns extraction document details with configuration fields and security mappings.
        """
        try:
            from src.domain.entities.extraction_file_detail import ExtractionFileDetail
            from src.domain.entities.file_configuration import FileConfiguration
            from src.domain.entities.file_configuration_field import FileConfigurationField
            
            logger.info(f"GetExtractDocumentApi: fileuid={fileuid}")
            
            # Initialize response object
            extraction_document_field = ExtractionDocumentField()
            
            # 1. Get ExtractionDocumentDetail by fileuid where isactive = true
            # C#: await _appDbContext.ExtractionDocumentDetail.FirstOrDefaultAsync(x => x.DocUID == docuId && x.IsActive == true)
            item = db.query(ExtractionFileDetail).filter(
                ExtractionFileDetail.fileuid == fileuid,
                ExtractionFileDetail.isactive == True
            ).first()
            
            if not item:
                logger.info(f"GetExtractDocumentApi: No active extraction document found for fileuid={fileuid}")
                return extraction_document_field.model_dump()
            
            # Convert entity to DTO
            extraction_document_field.extraction_document_detail = ExtractionFileDetailDTO.model_validate(item)
            
            # 2. If classification exists, get configuration details
            if item.classification and item.classification.strip():
                # Get DocumentConfiguration by classification name
                # C#: await _appDbContext.DocumentConfigurations.FirstOrDefaultAsync(x => x.ConfigurationName == item.Classification && x.IsActive == true)
                file_configuration = db.query(FileConfiguration).filter(
                    FileConfiguration.configuration_name == item.classification,
                    FileConfiguration.isactive == True
                ).first()
                
                if file_configuration:
                    extraction_document_field.configuration_id = file_configuration.fileconfigurationid
                    
                    # 3. Get all configuration fields for this configuration
                    # C#: await _appDbContext.DocumentConfigurationFields.Where(x => x.DocumentConfigurationId == documentConfiguration.Id && x.IsActive == true).ToListAsync()
                    file_configuration_fields = db.query(FileConfigurationField).filter(
                        FileConfigurationField.fileconfigurationid == file_configuration.fileconfigurationid,
                        FileConfigurationField.isactive == True
                    ).all()
                    
                    if file_configuration_fields:
                        # 4. Filter Object type fields
                        # C#: var objectFiledList = documentConfigurationFieldList.Where(x => x.DataType == DataTypes.Object).ToList()
                        object_fields = [f for f in file_configuration_fields if f.datatype == 'Object']
                        
                        if object_fields:
                            extraction_document_field.object_fields = [
                                FileConfigurationFieldDTO.model_validate(f) for f in object_fields
                            ]
                        
                        # Set all configuration fields
                        extraction_document_field.file_configuration_fields = [
                            FileConfigurationFieldDTO.model_validate(f) for f in file_configuration_fields
                        ]
                
                # 5. Get security mappings for specific classifications
                # C#: if (item.Classification == "Rage" || item.Classification == "BrokerageMSBilling")
                if item.classification in ["Rage", "BrokerageMSBilling"]:
                    security_mappings = self._get_file_security_by_fileuid(db, fileuid)
                    if security_mappings:
                        extraction_document_field.file_security_mappings = security_mappings
            
            # 6. Check for update document
            # C#: var documentUpdate = await _appDbContext.ExtractionDocumentDetail
            #     .Where(x => x.IsActive == true && x.Update_document_id == docuId)
            #     .Select(x => x.DocUID)
            #     .FirstOrDefaultAsync()
            update_document = db.query(ExtractionFileDetail.fileuid).filter(
                ExtractionFileDetail.isactive == True,
                ExtractionFileDetail.update_file_id == fileuid
            ).first()
            
            if update_document and update_document[0]:
                extraction_document_field.update_file_id = str(update_document[0])
            
            logger.info(f"GetExtractDocumentApi: Successfully retrieved extraction document for fileuid={fileuid}")
            return extraction_document_field.model_dump()
            
        except Exception as ex:
            logger.error(f"GetExtractDocumentApi error: {ex}", exc_info=True)
            raise Exception(f"An error occurred while retrieving data from the database: {str(ex)}")
    
    def _get_file_security_by_fileuid(
        self,
        db: Session,
        fileuid: UUID
    ) -> List[FileSecurityMappingDTO]:
        """
        Get file security mappings by fileuid.
        Replicates GetDocumentSecurityByDocuid from .NET.
        
        Note: The .NET code uses a stored procedure [alts].[GetDocumentSecurityByDocuid],
        but since stored procedures are not in use, we implement this as a direct query.
        """
        try:
            from src.domain.entities.file_security_mapping import FileSecurityMapping
            
            logger.info(f"GetFileSecurityByFileUID: fileuid={fileuid}")
            
            # Query file security mappings
            # This replicates the stored procedure logic
            security_mappings = db.query(FileSecurityMapping).filter(
                FileSecurityMapping.fileuid == fileuid,
                FileSecurityMapping.isactive == True
            ).all()
            
            # Convert to DTOs
            result = [FileSecurityMappingDTO.model_validate(mapping) for mapping in security_mappings]
            
            logger.info(f"GetFileSecurityByFileUID: Found {len(result)} security mappings")
            return result
            
        except Exception as ex:
            logger.error(f"GetFileSecurityByFileUID error: {ex}", exc_info=True)
            return []


    def get_extract_documents_by_file_uid(
        self,
        db: Session,
        fileuid: UUID
    ) -> List[Any]:
        """
        Replicates GetExtractDocumentsByDocUIDAsync logic.
        """
        try:
            from src.domain.entities.extract_file import ExtractFile
            logger.info(f"GetExtractDocumentsByDocUIDAsync: fileuid={fileuid}")
            
            results = db.query(ExtractFile).filter(
                ExtractFile.fileuid == fileuid,
                ExtractFile.isactive == True
            ).all()
            
            return results
        except Exception as ex:
            logger.error(f"GetExtractDocumentsByDocUIDAsync error: {ex}", exc_info=True)
            raise

    def add_document_comment(
        self,
        db: Session,
        fileuid: UUID,
        comment: str,
        created_by: str
    ) -> bool:
        """
        Updates FileManager record with a comment.
        """
        try:
            from src.domain.entities.file_manager import FileManager
            from datetime import datetime
            
            logger.info(f"AddDocumentComment: fileuid={fileuid}")
            
            # Fetch document
            document = db.query(FileManager).filter(
                FileManager.fileuid == fileuid
            ).first()
            
            if not document:
                logger.error(f"AddDocumentComment: Document not found for fileuid={fileuid}")
                return False
                
            # Update fields
            document.comments = comment
            document.statuscomment = "Comment Added"
            # document.updated = datetime.utcnow()
            # document.updatedby = created_by or "System"
            
            db.commit()
            logger.info(f"AddDocumentComment: Successfully updated fileuid={fileuid}")
            return True
            
        except Exception as ex:
            logger.error(f"AddDocumentComment error: {ex}", exc_info=True)
            db.rollback()
            return False

    def update_extract_document_api(
        self,
        db: Session,
        request: UpdateExtractFileRequest
    ) -> ResponseObjectModel:
        """
        Skeleton for UpdateExtractDocumentApi.
        """
        try:
            logger.info(f"UpdateExtractDocumentApi skeleton called for fileuid={request.extraction_document_detail.fileuid}")
            
            return ResponseObjectModel(
                result_code="SUCCESS",
                result_message="Update Document save successful (Skeleton)"
            )
        except Exception as ex:
            logger.error(f"UpdateExtractDocumentApi error: {ex}", exc_info=True)
            raise
