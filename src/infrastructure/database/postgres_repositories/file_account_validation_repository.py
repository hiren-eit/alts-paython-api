"""
PostgreSQL File Manager Repository
Clean implementation using separated query builder and result enricher.
"""

from src.domain.dtos.validation_detail_dto import ValidationDetailDto
from collections import defaultdict
from src.domain.entities.validation import Validation
from src.domain.dtos.file_account_validation_dto import FileAccountValidation
from src.domain.interfaces.file_account_validation_repository_interface import (
    IFileAccountValidationRepository,
)
from typing import List, Any, Dict

from sqlalchemy.orm import Session

from sqlalchemy import func, cast, String, case, and_, or_, distinct
from sqlalchemy.orm import Session
from uuid import UUID
from src.infrastructure.database.query_builders import (
    FileManagerQueryBuilder,
    FileManagerResultEnricher,
)
from src.infrastructure.logging.logger_manager import get_logger
from uuid import UUID

logger = get_logger(__name__)

BALANCE_CHECK_TYPES = {
    "opening_balance",
    "distribution",
    "capital_call",
}


class FileAccountvalidationRepository(IFileAccountValidationRepository):
    """PostgreSQL implementation of file account validation repository using SQLAlchemy ORM"""

    def get_file_account_details(
        self, db: Session, fileUID: UUID
    ) -> List[FileAccountValidation]:
        """
        Fetches and aggregates validation results for a given file, grouped by account.
        
        It performs the following steps:

        1. Retrieves all active validation records for the given file UID.
        2. Groups validation records by `accountsid`.
        3. For each account:
          - Calculates the total number of validations.
          - Calculates the number of passed validations
            (where status == "Success").
          - Separates validations into:
              a) Balance checks  -> validationtype in BalanceCheckTypes
              b) Other checks    -> validationtype not in BalanceCheckTypes
          - Maps each validation record to `ValidationDetailDto`.
        4. Returns a list of `FileAccountValidation` objects ordered by account SID.

        Parameters:
            db (Session):
                Active SQLAlchemy database session.
            fileUID (UUID):
                Unique identifier of the file whose validation details
                need to be retrieved.

        Returns:
            List[FileAccountValidation]:
                A list of account-level validation summaries, each containing:
                - account_sid
                - total_validation_count
                - passed_validation_count
                - balance_checks
                - other_checks

        Raises:
            Exception:
                Re-raises any exception encountered during data retrieval
                or transformation after logging the error.
        """
        try:
            # Fetch all active validation records for the given file
            validations = (
                db.query(Validation)
                .filter(Validation.fileuid == fileUID, Validation.isactive == True)
                .all()
            )

            # Group validations by account SID
            grouped: Dict[int, List[Validation]] = defaultdict(list)
            for v in validations:
                grouped[v.accountsid].append(v)

            result: List[FileAccountValidation] = []

            # Build account-level validation summary
            for account_sid in sorted(grouped.keys()):
                records = grouped[account_sid]

                total_count = len(records)
                passed_count = sum(1 for r in records if r.status == "Success")

                balance_checks: List[ValidationDetailDto] = []
                other_checks: List[ValidationDetailDto] = []

                # Categorize validations and map to DTOs
                for r in records:
                    dto = ValidationDetailDto(
                        validation_type=r.validationtype,
                        description=r.description,
                        newport_value=r.newportvalue,
                        extract_value=r.extractvalue,
                        difference=r.difference,
                        status=r.status,
                    )

                    if r.validationtype in BALANCE_CHECK_TYPES:
                        balance_checks.append(dto)
                    else:
                        other_checks.append(dto)

                result.append(
                    FileAccountValidation(
                        account_sid=account_sid,
                        total_validation_count=total_count,
                        passed_validation_count=passed_count,
                        balance_checks=balance_checks,
                        other_checks=other_checks,
                    )
                )

            return result

        except Exception as ex:
            logger.error(f"get_file_account_details error: {ex}", exc_info=True)
            raise
