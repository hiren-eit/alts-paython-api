"""
Get Account Data By FileUID Query Builder
Separates the query building logic from the repository for cleaner architecture.
This module handles all filter, sorting, and join logic for GetDocumentManager.
"""

from datetime import datetime
from typing import List, Dict, Optional
from uuid import UUID

from sqlalchemy import func, and_, or_, cast, String
from sqlalchemy.orm import Session, aliased

from src.domain.dtos.file_manager_dto import FileManagerFilter
from src.domain.entities.file_manager import FileManager
from src.domain.entities.extract_file import ExtractFile
from src.domain.entities.account_master import AccountMaster
from src.domain.entities.file_configuration import FileConfiguration
from src.domain.entities.firm_master import FirmMaster

class GetAccountDataByFileUID:
    def __init__(self, db: Session, fileuid: UUID):
        self.db = db
        # self.schema_type = schema_type
        self.fileuid = fileuid
        self._query = None

    def get_account_data_by_fileuid(self):
        query = (
            self.db.query(
                ExtractFile.fileuid,
                AccountMaster.account_uid,
                AccountMaster.accounts_id,
                AccountMaster.entity_uid,
                AccountMaster.firm_id,
                AccountMaster.entity_name,
                AccountMaster.account_name,
                AccountMaster.firm_name,
                AccountMaster.investor,
                AccountMaster.frequency,
                AccountMaster.delay,
                AccountMaster.annual_delay,
                AccountMaster.created,
                AccountMaster.updated
            )
            .join(
                AccountMaster,
                (ExtractFile.account_uid == AccountMaster.account_uid)
                & (ExtractFile.account_sid == AccountMaster.accounts_id)
            )
            .filter(
                ExtractFile.fileuid == self.fileuid,
                # ExtractFile.isactive == True
            )
        )
        return query.all()

    

    

