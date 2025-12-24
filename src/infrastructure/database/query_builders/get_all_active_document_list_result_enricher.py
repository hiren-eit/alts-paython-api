from sqlalchemy.orm import Session


class GetAllActiveDocumentListResultEnricher:
    def __init__(self, db: Session):
        self.db = db

    def enrich(self, results):
        """Enrich the results with additional info."""
        enriched_results = []
        
        for doc in results:
            enriched_doc = {
                'fileid': doc.fileid,
                'configuration_name': doc.configurationname,
                'description': doc.description,
                'sla_priority': doc.sla_priority,
                'sla_days': doc.sla_days,
                'schema_type': doc.schematype,
                'extraction': doc.extraction if doc.extraction else None,  # Enum to string
                'document_type_id': doc.filetypeid,
                'reason': doc.reason,
                'created': doc.created,
                'created_by': doc.createdby,
                'updated': doc.updated,
                'updated_by': doc.updatedby,
                'is_active': doc.isactive,
                'ingestion_code': doc.ingestioncode,
                'field_type': doc.fieldtype,
                'fields_collection': None,
                'logs_collection': None
            }
            enriched_results.append(enriched_doc)
        
        return enriched_results
    
    def enrich_master_config_type(self, results):
        """Enrich the results with additional info."""
        enriched_results = []

        for config_type in results:
            enriched_config_type = {
                'id': config_type.id,
                'displayname': config_type.displayname,
                'type': config_type.type
            }
            enriched_results.append(enriched_config_type)
        
        return enriched_results
