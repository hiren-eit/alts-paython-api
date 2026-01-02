from sqlalchemy.orm import Session


class GetAllActiveFileListResultEnricher:
    def __init__(self, db: Session):
        self.db = db

    def enrich(self, results):
        """Enrich the results with additional info."""
        enriched_results = []
        
        for file in results:
            enriched_file = {
                'fileid': file.fileid,
                'configuration_name': file.configurationname,
                'description': file.description,
                'sla_priority': file.sla_priority,
                'sla_days': file.sla_days,
                'schema_type': file.schematype,
                'extraction': file.extraction if file.extraction else None,  # Enum to string
                'file_type_id': file.filetypeid,
                'reason': file.reason,
                'created': file.created,
                'created_by': file.createdby,
                'updated': file.updated,
                'updated_by': file.updatedby,
                'is_active': file.isactive,
                'ingestion_code': file.ingestioncode,
                'field_type': file.fieldtype,
                'fields_collection': None,
                'logs_collection': None
            }
            enriched_results.append(enriched_file)
        
        return enriched_results
    
    def enrich_master_config_type(self, results):
        """Enrich the results with additional info."""
        enriched_results = []

        for config_type in results:
            enriched_config_type = {
                'id': config_type.masterconfigurationtypeid,
                'displayname': config_type.displayname,
                'type': config_type.type
            }
            enriched_results.append(enriched_config_type)
        
        return enriched_results
