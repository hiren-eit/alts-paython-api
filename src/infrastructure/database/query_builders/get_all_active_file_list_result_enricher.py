from sqlalchemy.orm import Session


class GetAllActiveFileListResultEnricher:
    def __init__(self, db: Session):
        self.db = db

    def enrich(self, results):
        """Enrich the results with additional info."""
        enriched_results = []

        for file in results:
            enriched_file = {
                "fileconfigurationid": file.fileid,
                "configurationname": file.configurationname,
                "description": file.description,
                "slapriority": file.sla_priority,
                "sladays": file.sla_days,
                "schematype": file.schematype,
                "extraction": (file.extraction if file.extraction else None),
                "filetypeid": file.filetypeid,
                "reason": file.reason,
                "created": file.created,
                "createdby": file.createdby,
                "updated": file.updated,
                "updatedby": file.updatedby,
                "isactive": file.isactive,
                "ingestioncode": file.ingestioncode,
                "fieldtype": file.fieldtype,
                "fields_collection": None,
                "logs_collection": None,
            }
            enriched_results.append(enriched_file)

        return enriched_results

    def enrich_master_config_type(self, results):
        """Enrich the results with additional info."""
        enriched_results = []

        for config_type in results:
            enriched_config_type = {
                "id": config_type.masterconfigurationtypeid,
                "displayname": config_type.displayname,
                "type": config_type.type,
            }
            enriched_results.append(enriched_config_type)

        return enriched_results
