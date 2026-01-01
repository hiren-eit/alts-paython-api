from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import asc, literal,desc

from src.domain.interfaces.account_details_repository_interface import IAccountDetailsRepository
from src.domain.entities.publishing_control import PublishingControl
from src.domain.dtos.account_details_dto import PublishingQueryParamsInput, PublishingRecordsResultResponse
from src.infrastructure.logging.logger_manager import get_logger
from src.utils.orderable_columns import ORDERABLE_COLUMNS

logger = get_logger(__name__)

class AccountDetailsRepository(IAccountDetailsRepository):
    """PostgreSQL implementation of AccountDetails repository"""

    def get_publishing_records(self, db: Session, parameters: PublishingQueryParamsInput) -> List[PublishingRecordsResultResponse]:
        """
        Replicates the GetPublishingRecords stored procedure logic.
        """
        try:
            logger.info(f"Postgres: GetPublishingRecords called for {parameters.accountid}")
            order_column = ORDERABLE_COLUMNS.get(parameters.orderbycolumn, PublishingControl.created)

            order_func = asc if parameters.ordertype.upper() == "ASC" else desc

            query = (
                db.query(
                    PublishingControl.publishingcontrolid,
                    PublishingControl.account_uid,
                    PublishingControl.pub_status,
                    PublishingControl.business_date,
                    PublishingControl.expected_date,
                    PublishingControl.received_date,
                    PublishingControl.file_type,
                    literal(None).label("marketvalue"),  # NULL AS MarketValue
                    PublishingControl.created,
                    PublishingControl.createdby,
                    PublishingControl.isactive,
                    PublishingControl.updated,
                    PublishingControl.updatedby,
                )
                .filter(PublishingControl.account_uid == parameters.accountid)
            )

            if parameters.filetype is not None:
                query = query.filter(PublishingControl.file_type == parameters.filetype)

            if parameters.pubstatus is not None:
                query = query.filter(PublishingControl.pub_status == parameters.pubstatus)

            query = query.order_by(order_func(order_column))
            result = query.all()
            return result
        except Exception as ex:
            logger.error(f"Postgres: GetPublishingRecords error: {ex}", exc_info=True)
            db.rollback()
            raise

