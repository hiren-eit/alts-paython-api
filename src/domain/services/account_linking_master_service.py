from sqlalchemy.orm import Session
from src.domain.dtos.account_linking_master_dto import AccountLinkingMaster, AccountLinkingMasterDataInputModel, BatchRuleUpdateRequest
from src.domain.interfaces.account_linking_master_repository_interface import IAccountLinkingMasterRepository
from uuid import UUID

class AccountLinkingMasterService:

    def __init__(self, repository: IAccountLinkingMasterRepository):
        self.repo = repository

    
    def get_account_linking_master_data(self, db: Session, inputModel: AccountLinkingMasterDataInputModel):
        """
            Returns account linking master data.
            Replicates the /GetAccountLinkingMasterData API & stored procedure logic.
        """
        return self.repo.get_account_linking_master_data(db, inputModel)
    

    def add_account_linking_master(self, db: Session, accountLinkingRecord: AccountLinkingMaster):
        """
            Save account linking master data.
            Replicates the /AddAccountLinkingMaster API & stored procedure logic.
        """
        return self.repo.add_account_linking_master(db, accountLinkingRecord)


    def updated_account_linking_master(self, db: Session, accountLinkingRecord: AccountLinkingMaster):
        """
            Update account linking master data.
            Replicates the /UpdatedAccountLinkingMaster API & stored procedure logic.
        """
        return self.repo.updated_account_linking_master(db, accountLinkingRecord)

    
    def delete_account_linking_master_by_id(self, db: Session, id: UUID):
        """
            Delete account linking master data by id.
            Replicates the /DeleteAccountLinkingMasterById API & stored procedure logic.
        """
        return self.repo.delete_account_linking_master_by_id(db, id)
    

    def get_account_linking_filter_by_field(self, db: Session, typeFilter: str, columnName: str):
        """
            Get account linking filter by field.
            Replicates the /GetAccountLinkingFilterByField API & stored procedure logic.
        """
        return self.repo.get_account_linking_filter_by_field(db, typeFilter, columnName)

    
    def toggle_rule(self, db: Session, rule: AccountLinkingMaster):
        """
            Toggle account linking rule.
            Replicates the /ToggleLinkingRule API & stored procedure logic.
        """
        return self.repo.toggle_rule(db, rule)
    

    def approve_rule(self, db: Session, rule: AccountLinkingMaster):
        """
            Approve account linking rule.
            Replicates the /ApproveRule API & stored procedure logic.
        """
        return self.repo.approve_rule(db, rule)

    
    def ignore_rule(self, db: Session, rule: AccountLinkingMaster):
        """
            Ignore account linking rule.
            Replicates the /IgnoreRule API & stored procedure logic.
        """
        return self.repo.ignore_rule(db, rule)

    
    def batch_update_rules(self, db: Session, request: BatchRuleUpdateRequest):
        """
            Update account linking rule in batch.
            Replicates the /BatchUpdateRules API & stored procedure logic.
        """
        return self.repo.batch_update_rules(db, request)
    

    def get_linking_master_rule_log_data(self, db: Session, id: str):
        """
            Get account linking rule log.
            Replicates the /GetLinkingMasterRuleLogApi API & stored procedure logic.
        """
        return self.repo.get_linking_master_rule_log_data(db, id)