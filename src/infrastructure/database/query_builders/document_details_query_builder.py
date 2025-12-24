from typing import Optional
from uuid import UUID
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
from src.domain.entities.file_configuration import FileConfiguration
from src.domain.entities.file_manager import FileManager

class DocumentDetailsQueryBuilder:
    """
    Query builder for file details by DocUID.
    Handles joins and base data only.
    """

    def __init__(self, db: Session, docuid: UUID):
        self.db = db
        self.docuid = docuid

    def get_file(self):
        D = FileManager
        DC = FileConfiguration

        return (
            self.db.query(D, DC.sla_days)
                .outerjoin(
                    DC,
                    and_(
                        DC.isactive.is_(True),
                        or_(
                            and_(
                                D.status.in_(["Captured", "Extract", "Update", "Failed"]),
                                DC.configurationname == D.filetypeproceesrule
                            ),
                            and_(
                                or_(
                                    D.status.in_(["Linked", "Approved"]),
                                    and_(
                                        D.status == "Failed",
                                        D.failurestage == "Failed Ingestion"
                                    )
                                ),
                                DC.configurationname == D.filetypegenai
                            )
                        )
                    )
                )
                .filter(
                    D.isactive.is_(True),
                    D.fileuid == self.docuid
                )
                .first()
        )


