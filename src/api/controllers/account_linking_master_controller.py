from importlib import import_module
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.domain.dtos.account_linking_master_dto import AccountLinkingMaster, AccountLinkingMasterDataInputModel, AccountLinkingMasterResponse, BatchRuleUpdateRequest
from src.domain.services.account_linking_master_service import AccountLinkingMasterService
from src.core.settings import get_connection_config
from src.infrastructure.database.connection_manager import get_db
from src.infrastructure.logging.logger_manager import get_logger
from uuid import UUID
from typing import Dict

DATABASE_URL, active_repository_path = get_connection_config()
AccountLinkingMasterRepository = import_module(f"{active_repository_path}.account_linking_master_repository").AccountLinkingMasterRepository

logger = get_logger(__name__)
router = APIRouter(prefix="/account-linking-master", tags=["AccountLinkingMaster"])

repository = AccountLinkingMasterRepository()
service = AccountLinkingMasterService(repository)

@router.post("/get-account-linking-master-data", response_model = AccountLinkingMasterResponse)
def get_account_linking_master_data(
        inputModel: AccountLinkingMasterDataInputModel,
        db: Session = Depends(get_db),
    ):
        """
        Returns account linking master data.
        Replicates the /GetAccountLinkingMasterData API & stored procedure logic.
        
        Returns:
                dict: {
                    "result_code": Optional[str],
                    "total": int,
                    "in_review_count": int,
                    "data": Optional[List[Dict]],
                    "result_message": Optional[str]
                }
        """
        return service.get_account_linking_master_data(db, inputModel)


@router.get("/get-account-linking-filter-by-field", response_model=dict)
def get_account_linking_filter_by_field(
        typeFilter: str,
        columnName: str,
        db: Session = Depends(get_db),
    ):
        """
            Get account linking filter by field.
            Replicates the /getAccountLinkingFilterByField API & stored procedure logic.
            Returns:
                dict: {
                    "result_code": Optional[str],
                    "total": int,
                    "in_review_count": int,
                    "data": Optional[List[Dict]],
                    "result_message": Optional[str]
                }
        """
        return service.get_account_linking_filter_by_field(db, typeFilter, columnName)


@router.post("/add-account-linking-master", response_model=bool)
def add_account_linking_master(
        accountLinkingRecord: AccountLinkingMaster,
        db: Session = Depends(get_db),
    ):
        """
            Save account linking master data.
            Replicates the /AddAccountLinkingMaster API & stored procedure logic.
        """
        return service.add_account_linking_master(db, accountLinkingRecord)


@router.post("/updated-account-linking-master", response_model=bool)
def updated_account_linking_master(
        accountLinkingRecord: AccountLinkingMaster,
        db: Session = Depends(get_db),
    ):
        """
            Update account linking master data.
            Replicates the /UpdatedAccountLinkingMaster API & stored procedure logic.
        """
        return service.updated_account_linking_master(db, accountLinkingRecord)


@router.delete("/delete-account-linking-master-by-id", response_model=bool)
def delete_account_linking_master_by_id(
        id: UUID,
        db: Session = Depends(get_db),
    ):
        """
            Delete account linking master data by id.
            Replicates the /DeleteAccountLinkingMasterById API & stored procedure logic.
        """
        return service.delete_account_linking_master_by_id(db, id)


@router.post("/toggle-linking-rule", response_model=str)
def toggle_rule(
        rule: AccountLinkingMaster,
        db: Session = Depends(get_db),
    ):
        """
            Toggle account linking rule.
            Replicates the /ToggleLinkingRule API & stored procedure logic.
        """
        return service.toggle_rule(db, rule)


@router.post("/approve-rule", response_model=str)
def approve_rule(
        rule: AccountLinkingMaster,
        db: Session = Depends(get_db),
    ):
        """
            Approve account linking rule.
            Replicates the /ApproveRule API & stored procedure logic.
        """
        return service.approve_rule(db, rule)


@router.post("/ignore-rule", response_model=str)
def ignore_rule(
        rule: AccountLinkingMaster,
        db: Session = Depends(get_db),
    ):
        """
            Ignore account linking rule.
            Replicates the /IgnoreRule API & stored procedure logic.
        """
        return service.ignore_rule(db, rule)


@router.post("/batch-update-rules", response_model=str)
def batch_update_rules(
        request: BatchRuleUpdateRequest,
        db: Session = Depends(get_db),
    ):
        """
            Update account linking rule in batch.
            Replicates the /BatchUpdateRules API & stored procedure logic.
        """
        return service.batch_update_rules(db, request)


@router.get("/get-linking-master-rule-log", response_model=AccountLinkingMasterResponse)
def get_linking_master_rule_log_data(
        id: str,
        db: Session = Depends(get_db),
    ):
        """
            Get account linking rule log.
            Replicates the /GetLinkingMasterRuleLogApi API & stored procedure logic.

            Returns:
                dict: {
                    "result_code": Optional[str],
                    "total": int,
                    "in_review_count": int,
                    "data": Optional[List[Dict]],
                    "result_message": Optional[str]
                }
        """
        return service.get_linking_master_rule_log_data(db, id)