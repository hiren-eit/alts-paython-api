from typing import List, Any, Dict
from sqlalchemy.orm import Session
from src.domain.dtos.account_linking_master_dto import AccountLinkingMaster, AccountLinkingMasterDataInputModel, BatchRuleUpdateRequest
from uuid import UUID

class IAccountLinkingMasterRepository:
    """Repository interface for AccountLinking"""

    def get_account_linking_master_data(
        self, 
        db: Session,
        inputModel: AccountLinkingMasterDataInputModel
    ) -> Dict:
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
        raise NotImplementedError
    

    def add_account_linking_master(
        self,
        db: Session,
        accountLinkingRecord: AccountLinkingMaster 
    ) -> bool:
        """
            Save account linking master data.
            Replicates the /AddAccountLinkingMaster API & stored procedure logic.
        """
        raise NotImplementedError


    def updated_account_linking_master(
        self,
        db: Session,
        accountLinkingRecord: AccountLinkingMaster 
    ) -> bool:
        """
            Update account linking master data.
            Replicates the /UpdatedAccountLinkingMaster API & stored procedure logic.
        """
        raise NotImplementedError

    
    def delete_account_linking_master_by_id(
        self,
        db: Session,
        id: UUID
    ) -> bool:
        """
            Delete account linking master data by id.
            Replicates the /DeleteAccountLinkingMasterById API & stored procedure logic.
        """
        raise NotImplementedError
    

    def get_account_linking_filter_by_field(
        self,
        db: Session,
        typeFilter: str,
        columnName: str
    ) -> dict:
        """
            Get account linking filter by field.
            Replicates the /GetAccountLinkingFilterByField API & stored procedure logic.
            Returns:
                dict: {
                    "result_code": Optional[str],
                    "total": int,
                    "in_review_count": int,
                    "data": Optional[List[Dict]],
                    "result_message": Optional[str]
                }
        """
        raise NotImplementedError

    
    def toggle_rule(
        self,
        db: Session,
        rule: AccountLinkingMaster
    ) -> str:
        """
            Toggle account linking rule.
            Replicates the /ToggleLinkingRule API & stored procedure logic.
        """
        raise NotImplementedError
    

    def approve_rule(
        self,
        db: Session,
        rule: AccountLinkingMaster
    ) -> str:
        """
            Approve account linking rule.
            Replicates the /ApproveRule API & stored procedure logic.
        """
        raise NotImplementedError

    
    def ignore_rule(
        self,
        db: Session,
        rule: AccountLinkingMaster
    ) -> str:
        """
            Ignore account linking rule.
            Replicates the /IgnoreRule API & stored procedure logic.
        """
        raise NotImplementedError

    
    def batch_update_rules(
        self,
        db: Session,
        request: BatchRuleUpdateRequest
    ) -> str:
        """
            Update account linking rule in batch.
            Replicates the /BatchUpdateRules API & stored procedure logic.
        """
        raise NotImplementedError
    

    def get_linking_master_rule_log_data(
        self,
        db: Session,
        id: str
    ) -> Dict:
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
        raise NotImplementedError