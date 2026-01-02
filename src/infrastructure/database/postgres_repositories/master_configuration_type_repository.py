from sqlalchemy.sql._elements_constructors import bindparam
from src.domain.interfaces.master_configuration_type_interface import (
    IMasterConfigurationTypeRepository,
)
from src.domain.entities.master_configuration_type import MasterConfigurationType
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)


class MasterConfigurationTypeRepository(IMasterConfigurationTypeRepository):
    """PostgreSQL implementation of Master Configuration Type repository"""

    def get_master_configuration_type(
        self, db: Session, type: str | None
    ) -> List[MasterConfigurationType]:
        try:
            sql = text(
                """
                SELECT
                    id,
                    "type",
                    displayname,
                    code,
                    isactive
                FROM frame.tbl_master_configuration_type
                WHERE
                    (:type IS NULL OR "type" = :type)
                    AND isactive = TRUE
                """
            ).bindparams(bindparam("type"))

            result = db.execute(sql, {"type": type}).mappings().all()

            return [
                MasterConfigurationType(
                    masterconfigurationtypeid=row["id"],
                    type=row["type"],
                    displayname=row["displayname"],
                    code=row["code"],
                    isactive=row["isactive"],
                )
                for row in result
            ]

        except Exception as ex:
            logger.error(f"get_master_configuration_type error: {ex}", exc_info=True)
            raise
